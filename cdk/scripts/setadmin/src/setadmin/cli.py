from argparse import ArgumentParser, Namespace
import json
import sys

import boto3

FUNCTION_ARN_OUTPUT = "RSSMusicPlayerSetAdminScriptArn"
STACK_NAME = "RSSMusicPlayerStack"


def parse_args() -> Namespace:
    parser = ArgumentParser(
        prog="setadmin",
        description=(
            "Mark or unmark a user as admin on an AWS deployment of Music Podcast "
            "Player"
        )
    )

    parser.add_argument("identifier", help="The username or email of the user")
    parser.add_argument(
        "-d", "--demote", action="store_true",
        help="Remove the user's admin status instead of making them an admin",
    )
    parser.add_argument(
        "-e", "--email", action="store_true",
        help="Indicates that the identifier is an email",
    )

    return parser.parse_args()


def find_identifier() -> str:
    cloudformation = boto3.client("cloudformation")
    
    outputs = cloudformation.describe_stacks(
        StackName=STACK_NAME
    )["Stacks"][0]["Outputs"]

    for output in outputs:
        if output["OutputKey"] == FUNCTION_ARN_OUTPUT:
            function_arn = output["OutputValue"]
            break
    else:
        print("Failed to find required outputs", file=sys.stderr)
        sys.exit(1)

    return function_arn


def main() -> None:
    args = parse_args()
  
    identifier_type = "email" if args.email else "username"
    event = {
        identifier_type: args.identifier,
        "admin": not args.demote,
    }

    function_arn = find_identifier()

    client = boto3.client("lambda")
    response = client.invoke(
        FunctionName=function_arn,
        InvocationType="RequestResponse",
        Payload=json.dumps(event),
    )

    response_text = response["Payload"].read().decode("UTF-8")
    response_json = json.loads(response_text)

    if "FunctionError" in response:
        print(f"Unexpected error:\n{response_json}", file=sys.stderr)
        sys.exit(1)

    if response_json["error"] is not None:
        print(
            f"An error of type {response_json["error"]} occurred:\n"
            f"{response_json["message"]}",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.demote:
        print("Successfully removed the user as an admin.")
    else:
        print("Successfully made the user an admin.")


if __name__ == "__main__":
    main()
