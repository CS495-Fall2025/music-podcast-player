# Run this script after deploying. This will happen automatically in CD.
import sys

import boto3

STACK_NAME = "RSSMusicPlayerStack"
SECRET_ARN_OUTPUT = "RSSMusicPlayerDatabaseSecretArn"

# When the migration handler runs, it is responsible for setting up IAM authentication,
# which it needs the database password to do. Without using a secrets manager endpoint,
# this is only possible if we put it in the environment of the Lambda when it runs. To
# mitigate risk of leaking it, we rotate it after deploying so that the secret in the 
# environment variable and cloudformation is no longer valid.
def rotate_database_secret() -> None:
    cloudformation = boto3.client("cloudformation")
    
    outputs = cloudformation.describe_stacks(
        StackName=STACK_NAME
    )["Stacks"][0]["Outputs"]

    for output in outputs:
        if output["OutputKey"] == SECRET_ARN_OUTPUT:
            secret_arn = output["OutputValue"]
            break
    else:
        import pdb; pdb.set_trace()
        print(f"Failed to find output {SECRET_ARN_OUTPUT}", file=sys.stderr)
        sys.exit(1)


    secretsmanager = boto3.client("secretsmanager")
    secretsmanager.rotate_secret(SecretId=secret_arn)

    print("Rotated database master password successfully")


def main() -> None:
    rotate_database_secret()


if __name__ == "__main__":
    main()
