from enum import Enum
import random
import time

import boto3
from botocore.exceptions import ClientError
from flask import current_app

from rss_music_api_service.auth.current_user import get_current_user_id


# Overall tokens are consumed by every request. Types of requests that have additional
# limits, for instance, to protect an external API, are also present in this enum and
# consumed only when that service is used.
class TokenType(Enum):
    OVERALL = "overall"
    PODCAST_INDEX = "podcast_index"


class UserType(Enum):
    # All users, public and authenticated, combined.
    GLOBAL = "global"
    # All unauthenticated users combined.
    PUBLIC = "public"
    # An individual authenticated user.
    USER = "user"


# Endpoints that consume tokens from other TokenTypes, beyond OVERALL. These endpoints
# have their own usage limits.
PROTECTED_ENDPOINTS = {"/search/feeds": [TokenType.PODCAST_INDEX]}

# Base delay before the first retry to update the tokens.
RETRY_BASE_DELAY = 0.025

# Number of attempts to try updating the token count before returning a rate limit
# error (as a failsafe).
MAX_ATTEMPTS = 3


# Returns True if successful, False if no tokens remaining.
def use_api_tokens_for_endpoint(endpoint: str) -> bool:
    for attempt in range(MAX_ATTEMPTS):
        try:
            return attempt_use_api_tokens_for_endpoint(endpoint)
        except ClientError as error:
            if not error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise

            if attempt == MAX_ATTEMPTS - 1:
                return False

            time.sleep(pick_retry_time(attempt))


def pick_retry_time(attempt: int) -> float:
    return RETRY_BASE_DELAY * random.uniform(0.5, 1.5) * (2.0 ** attempt)


def attempt_use_api_tokens_for_endpoint(endpoint: str) -> bool:
    token_types = PROTECTED_ENDPOINTS.get(endpoint, []).copy()
    token_types.append(TokenType.OVERALL)

    user_id = get_current_user_id(check_existence=False)
    if user_id is None:
        user_id = UserType.PUBLIC.value

    old_global_tokens = check_remaining_tokens(UserType.GLOBAL.value)
    old_user_tokens = check_remaining_tokens(user_id)

    global_tokens = old_global_tokens.copy()
    user_tokens = old_user_tokens.copy()

    for token_type in token_types:
        global_tokens[token_type.value] -= 1
        user_tokens[token_type.value] -= 1

        if global_tokens[token_type.value] < 0 or user_tokens[token_type.value] < 0:
            return False

    update_remaining_tokens(UserType.GLOBAL.value, global_tokens, old_global_tokens)
    update_remaining_tokens(user_id, user_tokens,  old_user_tokens)

    return True


def penalize_user_api_tokens(token_type: TokenType) -> None:
    if token_type.value not in current_app.config["TOKEN_PENALTY"]:
        raise ValueError(f"No penalty is defined for token type {token_type.value}")

    penalty = current_app.config["TOKEN_PENALTY"][token_type.value]

    user_id = get_current_user_id(check_existence=False)
    if user_id is None:
        user_id = UserType.PUBLIC.value

    old_global_tokens = check_remaining_tokens(UserType.GLOBAL.value)
    old_user_tokens = check_remaining_tokens(user_id)

    global_tokens = old_global_tokens.copy()
    user_tokens = old_user_tokens.copy()

    global_tokens[token_type.value] = max(global_tokens[token_type.value] - penalty, 0)
    user_tokens[token_type.value] = max(user_tokens[token_type.value] - penalty, 0)

    update_remaining_tokens(UserType.GLOBAL.value, global_tokens, old_global_tokens)
    update_remaining_tokens(user_id, user_tokens,  old_user_tokens)


def check_remaining_tokens(user_id: str) -> dict[str, int]:
    tokens = check_remaining_tokens_no_refill(user_id)

    if tokens is None or tokens["expiry"] <= int(time.time()):
        return refill_tokens(user_id)

    return tokens


def check_remaining_tokens_no_refill(user_id: str) -> dict[str, int] | None:
    table = get_token_table()
    response = table.get_item(
        Key={"user_id": user_id},
    )

    if "Item" not in response:
        return None
    else:
        token_entry = response["Item"]

    return token_entry


def refill_tokens(user_id: str) -> dict[str, int]:
    match user_id:
        case UserType.GLOBAL.value:
            token_entry = get_token_refill_values(UserType.GLOBAL)
        case UserType.PUBLIC.value:
            token_entry = get_token_refill_values(UserType.PUBLIC)
        case _:
            token_entry = get_token_refill_values(UserType.USER)

    token_entry |= {
        "expiry": int(time.time()) + current_app.config["TOKEN_REFILL_SECONDS"],
        "user_id": user_id,
    }

    old_tokens = check_remaining_tokens_no_refill(user_id)
    if old_tokens is None:
        old_tokens = {}

    update_remaining_tokens(user_id, token_entry, old_tokens)

    return token_entry


def get_token_refill_values(user_type: UserType) -> dict[str, int]:
    return current_app.config["API_TOKENS_PER_REFILL"][user_type.value].copy()


def update_remaining_tokens(user_id: str, token_values: dict, old_values: dict) -> None:
    table = get_token_table()

    if "user_id" in token_values:
        del token_values["user_id"]
    
    if "user_id" in old_values:
        del old_values["user_id"]

    conditions = []
    attrib_names = {}
    attrib_values = {}
    for index, (key, value) in enumerate(old_values.items()):
        conditions.append(f"#{index} = :old_{index}")
        attrib_names[f"#{index}"] = key
        attrib_values[f":old_{index}"] = value

    final_condition = "attribute_not_exists(overall)"
    if conditions:
        final_condition += " OR " + " AND ".join(conditions)

    expr_kwargs = {}
    if conditions:
        expr_kwargs = {
            "ExpressionAttributeNames": attrib_names,
            "ExpressionAttributeValues": attrib_values,
        }

    # This will fail with a ClientError if the condition (that the tokens are what they
    # were when we read them) is not true at the time of attempting the write. The check
    # and write together are atomic.
    table.put_item(
        Item={"user_id": user_id} | token_values,
        ConditionExpression=final_condition,
        **expr_kwargs,
    )


def get_token_table():
    url_override = current_app.config.get("DYNAMODB_URL")
    if url_override:
        dynamodb = boto3.resource("dynamodb", endpoint_url=url_override)
    else:
        dynamodb = boto3.resource("dynamodb")

    return dynamodb.Table(current_app.config["TOKEN_TABLE_NAME"])
