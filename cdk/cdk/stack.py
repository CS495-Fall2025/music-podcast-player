from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    RemovalPolicy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3 as s3
)
from constructs import Construct

class RSSMusicPlayerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        frontend_bucket = self._make_frontend_bucket()
        frontend_distribution = self._make_frontend_distribution(frontend_bucket)

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
        behavior = cloudfront.BehaviorOptions(
            origin=origins.S3BucketOrigin(bucket),
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
            description="The URL of the frontend"
        )

        return distribution
