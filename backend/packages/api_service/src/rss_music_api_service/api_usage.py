from enum import Enum
import time

import boto3
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
PROTECTED_ENDPOINTS = {
    "/search/feeds": [TokenType.PODCAST_INDEX]
}


# Returns True if successful, False if no tokens remaining.
def use_api_tokens_for_endpoint(endpoint: str) -> bool:
    token_types = PROTECTED_ENDPOINTS.get(endpoint, []).copy()
    token_types.append(TokenType.OVERALL)

    user_id = get_current_user_id(check_existence=False)
    if user_id is None:
        user_id = UserType.PUBLIC.value

    global_tokens = check_remaining_tokens(UserType.GLOBAL.value)
    user_tokens = check_remaining_tokens(user_id)

    for token_type in token_types:
        global_tokens[token_type.value] -= 1
        user_tokens[token_type.value] -= 1

        if global_tokens[token_type.value] < 0 or user_tokens[token_type.value] < 0:
            return False

    update_remaining_tokens(UserType.GLOBAL.value, global_tokens)
    update_remaining_tokens(user_id, user_tokens)

    return True


def penalize_user_api_tokens(token_type: TokenType) -> None:
    if token_type.value not in current_app.config["TOKEN_PENALTY"]:
        raise ValueError(f"No penalty is defined for token type {token_type.value}")

    penalty = current_app.config["TOKEN_PENALTY"][token_type.value]

    user_id = get_current_user_id(check_existence=False)
    if user_id is None:
        user_id = UserType.PUBLIC.value

    global_tokens = check_remaining_tokens(UserType.GLOBAL.value)
    user_tokens = check_remaining_tokens(user_id)

    global_tokens[token_type.value] = max(global_tokens[token_type.value] - penalty, 0) 
    user_tokens[token_type.value] = max(user_tokens[token_type.value] - penalty, 0) 
    
    update_remaining_tokens(UserType.GLOBAL.value, global_tokens)
    update_remaining_tokens(user_id, user_tokens)


def check_remaining_tokens(user_id: str) -> dict[str, int]:
    table = get_token_table()
    response = table.get_item(
        Key={"user_id": user_id},
    )

    if "Item" not in response or response["Item"]["expiry"] <= int(time.time()):
        token_entry = refill_tokens(user_id)
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
    update_remaining_tokens(user_id, token_entry)

    return token_entry


def get_token_refill_values(user_type: UserType) -> dict[str, int]:
    return current_app.config["API_TOKENS_PER_REFILL"][user_type.value].copy()


def update_remaining_tokens(user_id: str, token_values: dict) -> None:
    table = get_token_table()

    if "user_id" in token_values:
        del token_values["user_id"]

    table.put_item(
        Item={"user_id": user_id} | token_values,
    )


def get_token_table():
    url_override = current_app.config.get("DYNAMODB_URL")
    if url_override:
        dynamodb = boto3.resource("dynamodb", endpoint_url=url_override)
    else:
        dynamodb = boto3.resource("dynamodb")

    return dynamodb.Table(current_app.config["TOKEN_TABLE_NAME"])
