import os
from pathlib import Path
import json

from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    RemovalPolicy,
    aws_apigateway as apigw,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_rds as rds,
    aws_ssm as ssm,
    aws_s3 as s3,
    aws_s3_deployment as s3_deploy,
)
from constructs import Construct

BACKEND_PATH = Path(__file__).parent.parent.parent / "backend"
FRONTEND_PATH = Path(__file__).parent.parent.parent / "frontend"
BACKEND_BUILD = os.environ.get(
    "BACKEND_BUILD_PATH", str(BACKEND_PATH / "lambda_build/backend_build.zip")
)
FRONTEND_BUILD = os.environ.get("FRONTEND_BUILD_PATH", str(FRONTEND_PATH / "dist"))


class RSSMusicPlayerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Things in this VPC can reach the database, but not the outside internet.
        # database_vpc = ec2.Vpc(self, "RSSMusicPlayerDatabaseVpc", max_azs=3)
        # database = self._make_database(database_vpc)

        frontend_bucket = self._make_frontend_bucket()
        frontend_distribution = self._make_frontend_distribution(frontend_bucket)

        # For when we split the backend.
        # database_function = self._make_database_function(
        #    database, database_vpc
        # )
        backend_function = self._make_backend_function(
            frontend_distribution.domain_name
        )

        backend_rest_api = self._make_rest_api(backend_function)

        self._deploy_frontend(frontend_bucket, backend_rest_api.url)

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

    def _make_frontend_distribution(self, bucket: s3.Bucket) -> cloudfront.Distribution:
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

    def _make_database_function(self, database, database_vpc) -> _lambda.Function:
        function = _lambda.Function(
            self,
            "RSSMusicPlayerBackendDatabaseFunction",
            # code=_lambda.Code.from_asset(),
            runtime=_lambda.Runtime.PYTHON_3_12,
            # handler="lambda_handler.handler",
            memory_size=256,
            architecture=_lambda.Architecture.ARM_64,
            environment={
                "DATABASE_CONNECTION_PARTIAL": "postgresql://{user}:{password}@"
                f"{database.db_instance_endpoint_address}:"
                f"{database.db_instance_endpoint_port}",
                "DATABASE_SECRET_ARN": database.secret.secret_arn,
            },
            vpc=database_vpc,
            timeout=Duration.seconds(3),
        )

        database.secret.grant_read(function)

        return function

    def _make_backend_function(self, frontend_domain) -> _lambda.Function:
        # These are REFERENCES to keys that MUST be created manually. AWS doesn't
        # support creating SecureString parameters through the CDK, and we'd need to set
        # the values manually anyways.
        backend_secrets = [
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
        ]

        function = _lambda.Function(
            self,
            "RSSMusicPlayerBackendInternetFunction",
            code=_lambda.Code.from_asset(str(BACKEND_BUILD)),
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_handler.handler",
            memory_size=512,
            architecture=_lambda.Architecture.ARM_64,
            environment={
                "RSS_PLAYER_ALLOWED_ORIGINS": f"https://{frontend_domain}",
                "PODCAST_INDEX_KEY_ROUTE": "/rss-music-player/podcast-index-api/key",
                "PODCAST_INDEX_SECRET_ROUTE": "/rss-music-player/podcast-index-api/secret",
            },
            timeout=Duration.seconds(3),
        )

        for secret in backend_secrets:
            secret.grant_read(function)

        return function

    def _make_rest_api(self, function: _lambda.Function) -> apigw.LambdaRestApi:
        api = apigw.LambdaRestApi(
            self,
            "RSSMusicPlayerBackendRestApi",
            handler=function,
            proxy=True,
        )

        CfnOutput(
            self,
            "RSSMusicPlayerBackendURL",
            value=api.url,
        )

        return api

    def _deploy_frontend(
        self, bucket: s3.Bucket, api_url: str
    ) -> s3_deploy.BucketDeployment:
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
        )

        return deployment

    def _make_database(self, database_vpc: ec2.Vpc) -> rds.DatabaseInstance:
        security_group = ec2.SecurityGroup.from_security_group_id(
            self, "DefaultSG", database_vpc.vpc_default_security_group
        )

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
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[security_group],
            multi_az=False,
            allocated_storage=20,
            publicly_accessible=False,
            storage_encrypted=True,
            credentials=rds.Credentials.from_generated_secret(
                username="rssmusicplayer"
            ),
            backup_retention=Duration.days(1),
            removal_policy=RemovalPolicy.DESTROY,
        )

        database.connections.allow_default_port_from_any_ipv4(
            description="Necessary to allow backend to connect"
        )

        database.add_rotation_single_user(automatically_after=Duration.days(30))

        CfnOutput(
            self,
            "RSSMusicPlayerDatabaseEndpoint",
            value=(
                f"{database.db_instance_endpoint_address}:"
                f"{database.db_instance_endpoint_port}"
            ),
        )

        return database
