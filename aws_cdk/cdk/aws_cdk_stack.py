from pathlib import Path

from aws_cdk import (
    Duration,
    Stack,
    aws_apigateway,
    aws_lambda,
)
from constructs import Construct

LAMBDA_FUNCTION_NAME = "RSSMusicPlayerBackend"
APIG_ENDPOINT_NAME = "RSSMusicPlayerEndpoint"

BACKEND_PATH = Path(__file__).parent.parent.parent / "backend"


class BackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_function = self._make_lambda_function()

    def _make_lambda_function(self) -> aws_lambda.Function:
        return aws_lambda.Function(
            self,
            LAMBDA_FUNCTION_NAME,
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            handler="lambda_app.lambda_handler",
            code=aws_lambda.Code.from_asset(
                str(BACKEND_PATH),
                bundling={
                    "image": aws_lambda.Runtime.PYTHON_3_12.bundling_image,
                    "command": [
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output "
                        "&& pip install . -t /asset-output "
                        "&& cp src/lambda_app.py /asset-output"
                    ]
                },
            ),
            timeout=Duration.seconds(3),
            memory_size=256,
        )

    def _make_gateway_endpoint(
            self, function: aws_lambda.Function
    ) -> aws_apigateway.LambdaRestApi:
        return aws_apigateway.LambdaRestApi(
            self,
            APIG_ENDPOINT_NAME,
            handler=function,
            proxy=True
        )
