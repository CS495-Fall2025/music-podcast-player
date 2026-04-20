import json
import sys

import boto3

from utils import passwords

STACK_NAME = "RSSMusicPlayerStack"
DATABASE_ID_OUTPUT = "RSSMusicPlayerDatabaseIdentifier"

# Around 64 base64 chars.
PASSWORD_LENGTH = 48


def find_identifier() -> str:
    cloudformation = boto3.client("cloudformation")
    
    outputs = cloudformation.describe_stacks(
        StackName=STACK_NAME
    )["Stacks"][0]["Outputs"]

    for output in outputs:
        if output["OutputKey"] == DATABASE_ID_OUTPUT:
            database_id = output["OutputValue"]
            break
    else:
        print("Failed to find required outputs", file=sys.stderr)
        sys.exit(1)

    return database_id


def rotate_secret_on_db(password: str, db_id: str) -> None:
    rds = boto3.client("rds")

    rds.modify_db_instance(
        DBInstanceIdentifier=db_id,
        MasterUserPassword=password,
        ApplyImmediately=True,
    )


# This is a custom solution for rotating the master password without requiring
# SecretsManager, which would in turn require a VPC endpoint and double the current cost
# of hosting our app.
def main() -> None:
    print("Fetching identifiers")
    database_id = find_identifier()
    password = passwords.generate_db_secret()

    print("Applying to RDS")
    rotate_secret_on_db(password, database_id)
    
    print("Rotated database master password successfully")


if __name__ == "__main__":
    main()
