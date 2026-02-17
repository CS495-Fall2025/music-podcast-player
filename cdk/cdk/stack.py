import hashlib
import os
from pathlib import Path
import json

from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    RemovalPolicy,
    CustomResource,
    aws_apigatewayv2 as apigw2,
    aws_apigatewayv2_integrations as apigw2_int,
    aws_apigatewayv2_authorizers as apigw2_auth,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_rds as rds,
    aws_ssm as ssm,
    aws_s3 as s3,
    aws_s3_deployment as s3_deploy,
    custom_resources as cr,
)
from constructs import Construct

BACKEND_PATH = Path(__file__).parent.parent.parent / "backend"
FRONTEND_PATH = Path(__file__).parent.parent.parent / "frontend"
BACKEND_BUILD = Path(os.environ.get("BACKEND_BUILD_PATH", BACKEND_PATH / "builds"))
FRONTEND_BUILD = os.environ.get("FRONTEND_BUILD_PATH", FRONTEND_PATH / "dist")

API_SERVICE_PREFIX = "/api/v1"


class RSSMusicPlayerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Things in this VPC can reach the database, but not the outside internet.
        database_vpc = self._make_database_vpc()
        security_groups = self._make_security_groups(database_vpc)
        database = self._make_database(database_vpc, security_groups["database"])

        migration_function = self._make_migration_function(
            database, database_vpc, security_groups["function"]
        )
        self._make_migration_resource(migration_function, database)

        frontend_bucket = self._make_frontend_bucket()
        distribution = self._make_public_distribution(frontend_bucket)

        # For when we split the backend.
        db_service_function = self._make_db_service_function(
            database, database_vpc, security_groups["function"]
        )
        db_service_api = self._make_db_service_api(db_service_function)

        api_service_function = self._make_api_service_function(
            distribution.domain_name,
            db_service_api,
        )
        api_service_api = self._make_api_service_api(api_service_function)
        self._attach_api_service_to_distribution(api_service_api, distribution)

        self._deploy_frontend(
            frontend_bucket,
            distribution,
            f"https://{distribution.distribution_domain_name}{API_SERVICE_PREFIX}",
        )

    def _make_frontend_bucket(self) -> s3.Bucket:
        bucket = s3.Bucket(
            self,
            "RSSMusicPlayerFrontendBucket",
            # Okay because we will rebuild the frontend on redeploy. Consider RETAIN for
            # production.
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        CfnOutput(
            self,
            "RSSMusicPlayerFrontendBucketName",
            value=bucket.bucket_name,
            description="The name of the S3 bucket for the frontend",
        )

        return bucket

    def _make_public_distribution(self, bucket: s3.Bucket) -> cloudfront.Distribution:
        access_control = cloudfront.S3OriginAccessControl(
            self,
            "RSSMusicPlayerFrontendBucketOAC",
            signing=cloudfront.Signing.SIGV4_ALWAYS,
        )

        origin = origins.S3BucketOrigin.with_origin_access_control(
            bucket, origin_access_control=access_control
        )

        behavior = cloudfront.BehaviorOptions(
            origin=origin,
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        )

        # Have Vue's router handle page routing.
        spa_responses = [
            cloudfront.ErrorResponse(
                http_status=403,
                response_http_status=200,
                response_page_path="/index.html",
                ttl=Duration.seconds(0),
            ),
            cloudfront.ErrorResponse(
                http_status=404,
                response_http_status=200,
                response_page_path="/index.html",
                ttl=Duration.seconds(0),
            ),
        ]

        distribution = cloudfront.Distribution(
            self,
            "RSSMusicPlayerFrontendDistribution",
            default_behavior=behavior,
            default_root_object="index.html",
            error_responses=spa_responses,
        )

        CfnOutput(
            self,
            "RSSMusicPlayerFrontendURL",
            value=f"https://{distribution.domain_name}",
            description="The URL of the frontend",
        )

        return distribution

    def _make_migration_function(
        self,
        database: rds.DatabaseInstance,
        database_vpc: ec2.Vpc,
        group: ec2.SecurityGroup,
    ) -> _lambda.Function:
        code = _lambda.Code.from_asset(
            str(BACKEND_BUILD / "migration-handler-build.zip")
        )

        function = _lambda.Function(
            self,
            "RSSMusicPlayerMigrationFunction",
            code=code,
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_handler.handler",
            memory_size=256,
            architecture=_lambda.Architecture.ARM_64,
            environment={
                "DATABASE_URL_PARTIAL": "postgresql://{user}:{password}@"
                f"{database.db_instance_endpoint_address}:"
                f"{database.db_instance_endpoint_port}",
                "DATABASE_SECRET_ARN": database.secret.secret_arn,
            },
            vpc=database_vpc,
            security_groups=[group],
            timeout=Duration.seconds(5),
        )

        database.secret.grant_read(function)

        return function

    def _make_migration_resource(
        self,
        migration_function: _lambda.Function,
        database: rds.DatabaseInstance,
    ) -> cr.AwsCustomResource:
        provider = cr.Provider(
            self,
            "RSSMusicPlayerMigrationProvider",
            on_event_handler=migration_function,
        )

        migration_resource = CustomResource(  # cr.AwsCustomResource(
            self,
            "RSSMusicPlayerMigrationRunner",
            service_token=provider.service_token,
        )

        migration_resource.node.add_dependency(database)

        return migration_resource

    def _make_db_service_function(
        self,
        database: rds.DatabaseInstance,
        database_vpc: ec2.Vpc,
        group: ec2.SecurityGroup,
    ) -> _lambda.Function:
        function = _lambda.Function(
            self,
            "RSSMusicPlayerDatabaseServiceFunction",
            code=_lambda.Code.from_asset(str(BACKEND_BUILD / "db-service-build.zip")),
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_handler.handler",
            memory_size=256,
            architecture=_lambda.Architecture.ARM_64,
            environment={
                "DATABASE_URL_PARTIAL": "postgresql://{user}:{password}@"
                f"{database.db_instance_endpoint_address}:"
                f"{database.db_instance_endpoint_port}",
                "DATABASE_SECRET_ARN": database.secret.secret_arn,
            },
            vpc=database_vpc,
            security_groups=[group],
            timeout=Duration.seconds(5),
        )

        database.secret.grant_read(function)

        return function

    def _make_db_service_api(self, function: _lambda.Function) -> apigw2.HttpApi:
        api = apigw2.HttpApi(
            self,
            "RSSMusicPlayerDatabaseServiceApi",
            default_authorizer=apigw2_auth.HttpIamAuthorizer(),
        )

        api.add_routes(
            path="/{proxy+}",
            methods=[apigw2.HttpMethod.ANY],
            integration=apigw2_int.HttpLambdaIntegration(
                "RSSMusicPlayerDatabaseServiceApiIntegration", handler=function
            ),
        )

        # api = apigw2.HttpApi(
        #    self,
        #    "RSSMusicPlayerDatabaseServiceApi",
        #    handler=function,
        #    endpoint_configuration=apigw.EndpointConfiguration(
        #        types=[
        #            apigw.EndpointType.REGIONAL,
        #        ],
        #    ),
        #    default_method_options=apigw.MethodOptions(
        #        authorization_type=apigw.AuthorizationType.IAM,
        #    ),
        #    proxy=True,
        # )

        CfnOutput(
            self,
            "RSSMusicPlayerDatabaseServiceURL",
            value=api.url,
        )

        return api

    def _make_api_service_function(
        self, frontend_domain, db_service_api
    ) -> _lambda.Function:
        # These are REFERENCES to keys that MUST be created manually. AWS doesn't
        # support creating SecureString parameters through the CDK, and we'd need to set
        # the values manually anyways.
        secrets = [
            ssm.StringParameter.from_secure_string_parameter_attributes(
                self,
                "RSSMusicPlayerPodcastIndexAPIKey",
                parameter_name="/rss-music-player/podcast-index-api/key",
            ),
            ssm.StringParameter.from_secure_string_parameter_attributes(
                self,
                "RSSMusicPlayerPodcastIndexAPISecret",
                parameter_name="/rss-music-player/podcast-index-api/secret",
            ),
            ssm.StringParameter.from_secure_string_parameter_attributes(
                self,
                "RSSMusicPlayerJwtSecretKey",
                parameter_name="/rss-music-player/jwt/key",
            ),
        ]

        function = _lambda.Function(
            self,
            "RSSMusicPlayerApiServiceFunction",
            code=_lambda.Code.from_asset(str(BACKEND_BUILD / "api-service-build.zip")),
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_handler.handler",
            memory_size=512,
            architecture=_lambda.Architecture.ARM_64,
            environment={
                "RSS_PLAYER_ALLOWED_ORIGINS": f"https://{frontend_domain}",
                "RSS_PLAYER_ENVIRONMENT": "production",
                "RSS_PLAYER_DB_SERVICE_URL": db_service_api.url,
                "RSS_PLAYER_API_ROOT": API_SERVICE_PREFIX,
                "PODCAST_INDEX_KEY_ROUTE": "/rss-music-player/podcast-index-api/key",
                "PODCAST_INDEX_SECRET_ROUTE": "/rss-music-player/podcast-index-api/secret",
                "SECRET_KEY_ROUTE": "/rss-music-player/jwt/key",
            },
            timeout=Duration.seconds(12),
        )

        for secret in secrets:
            secret.grant_read(function)

        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["execute-api:Invoke"],
                resources=[db_service_api.arn_for_execute_api()],
            )
        )

        return function

    def _make_api_service_api(self, function: _lambda.Function) -> apigw2.HttpApi:
        api = apigw2.HttpApi(
            self,
            "RSSMusicPlayerApiServiceApi",
        )

        api.add_routes(
            path=API_SERVICE_PREFIX + "/{proxy+}",
            methods=[apigw2.HttpMethod.ANY],
            integration=apigw2_int.HttpLambdaIntegration(
                "RSSMusicPlayerApiServiceApiIntegration", handler=function
            ),
        )

        CfnOutput(
            self,
            "RSSMusicPlayerApiServiceURL",
            value=api.url,
        )

        return api

    def _attach_api_service_to_distribution(
        self, api: apigw2.HttpApi, dist: cloudfront.Distribution
    ) -> None:
        api_origin = origins.HttpOrigin(
            domain_name=f"{api.api_id}.execute-api.{self.region}.amazonaws.com",
        )

        dist.add_behavior(
            path_pattern=f"{API_SERVICE_PREFIX}/*",
            origin=api_origin,
            cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
            origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
            allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        )

    def _deploy_frontend(
        self, bucket: s3.Bucket, distribution: cloudfront.Distribution, api_url: str
    ) -> s3_deploy.BucketDeployment:
        if api_url.endswith("/"):
            api_url = api_url[0:-1]

        config = {
            "backendUrl": api_url,
        }

        deployment = s3_deploy.BucketDeployment(
            self,
            "RSSMusicPlayerFrontendDeployment",
            sources=[
                s3_deploy.Source.asset(str(FRONTEND_BUILD)),
                s3_deploy.Source.data(
                    "config.json",
                    json.dumps(config),
                ),
            ],
            destination_bucket=bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )

        return deployment

    def _make_database(
        self, database_vpc: ec2.Vpc, group: ec2.SecurityGroup
    ) -> rds.DatabaseInstance:
        database = rds.DatabaseInstance(
            self,
            "RSSMusicPlayerDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_17
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE4_GRAVITON,
                ec2.InstanceSize.MICRO,
            ),
            vpc=database_vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            security_groups=[group],
            multi_az=False,
            allocated_storage=20,
            publicly_accessible=False,
            storage_encrypted=True,
            credentials=rds.Credentials.from_generated_secret(
                username="rssmusicplayer"
            ),
            database_name="rssmusicplayer",
            backup_retention=Duration.days(1),
            removal_policy=RemovalPolicy.DESTROY,
        )

        database.connections.allow_default_port_from_any_ipv4(
            description="Necessary to allow backend to connect"
        )

        # database.add_rotation_single_user(automatically_after=Duration.days(30))

        CfnOutput(
            self,
            "RSSMusicPlayerDatabaseEndpoint",
            value=(
                f"{database.db_instance_endpoint_address}:"
                f"{database.db_instance_endpoint_port}"
            ),
        )

        return database

    def _make_database_vpc(self) -> ec2.Vpc:
        vpc = ec2.Vpc(self, "RSSMusicPlayerDatabaseVpc", max_azs=3, nat_gateways=0)

        ec2.InterfaceVpcEndpoint(
            self,
            "RSSMusicPlayerDatabaseVpcSecretsEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
            ),
        )

        return vpc

    def _get_file_hash(self, path: Path) -> str:
        hash = hashlib.sha256()

        with open(path, "rb") as file:
            while chunk := file.read(2048):
                hash.update(chunk)

        return hash.hexdigest()

    def _make_security_groups(self, vpc: ec2.Vpc) -> dict[str, ec2.SecurityGroup]:
        groups = {
            "database": ec2.SecurityGroup(
                self,
                "RSSMusicPlayerDatabaseSecurityGroup",
                vpc=vpc,
                allow_all_outbound=False,
            ),
            "function": ec2.SecurityGroup(
                self,
                "RSSMusicPlayerFunctionSecurityGroup",
                vpc=vpc,
                allow_all_outbound=True,
            ),
            "endpoint": ec2.SecurityGroup(
                self,
                "RSSMusicPlayerEndpointSecurityGroup",
                vpc=vpc,
                allow_all_outbound=True,
            ),
        }

        groups["database"].add_ingress_rule(
            peer=groups["function"],
            connection=ec2.Port.tcp(5432),
        )

        groups["endpoint"].add_ingress_rule(
            peer=groups["function"],
            connection=ec2.Port.tcp(443),
        )

        return groups
