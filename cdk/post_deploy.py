# Run this script after deploying. This will happen automatically in CD.
import base64
import json
import secrets
import sys

import boto3

STACK_NAME = "RSSMusicPlayerStack"
SECRET_ARN_OUTPUT = "RSSMusicPlayerDatabaseSecretArn"
DATABASE_ID_OUTPUT = "RSSMusicPlayerDatabaseIdentifier"

# Around 64 base64 chars.
PASSWORD_LENGTH = 48


def find_identifiers() -> tuple[str, str]:
    cloudformation = boto3.client("cloudformation")
    
    outputs = cloudformation.describe_stacks(
        StackName=STACK_NAME
    )["Stacks"][0]["Outputs"]

    secret_arn = None
    database_id = None
    for output in outputs:
        if output["OutputKey"] == SECRET_ARN_OUTPUT:
            secret_arn = output["OutputValue"]
        if output["OutputKey"] == DATABASE_ID_OUTPUT:
            database_id = output["OutputValue"]
    
    if secret_arn is None or database_id is None:
        print("Failed to find required outputs", file=sys.stderr)
        sys.exit(1)

    return database_id, secret_arn


def rotate_secret_on_db(password: str, db_id: str) -> None:
    rds = boto3.client("rds")

    rds.modify_db_instance(
        DBInstanceIdentifier=db_id,
        MasterUserPassword=password,
        ApplyImmediately=True,
    )


def rotate_secret_on_sm(password: str, secret_arn: str) -> None:
    secretsmanager = boto3.client("secretsmanager")

    secret = json.loads(
        secretsmanager.get_secret_value(SecretId=secret_arn)["SecretString"]
    )

    secret["password"] = password

    secrets.update_secret(
        SecretId=secret_arn,
        SecretString=json.dumps(secret),
    )


def _make_password() -> str:
    password_bytes = secrets.token_bytes(PASSWORD_LENGTH)
    password = base64.urlsafe_b64encode(password_bytes).decode("UTF-8")
    return password


# This is a custom solution for rotating the master password without requiring a
# SecretsManager endpoint.
def main() -> None:
    print("Fetching identifiers")
    database_id, secret_arn = find_identifiers()

    password = _make_password()

    print("Setting secret on RDS")
    rotate_secret_on_db(password, database_id)
    
    print("Setting secret on SecretsManager")
    rotate_secret_on_sm(password, secret_arn)

    print("Rotated database master password successfully")


if __name__ == "__main__":
    main()
