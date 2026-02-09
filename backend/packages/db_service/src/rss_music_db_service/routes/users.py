from json import JSONDecodeError

from fastapi import status, APIRouter, Request
from fastapi.responses import JSONResponse
from marshmallow import ValidationError

from rss_music_db_service_schemas import ErrorResponse, ErrorType
import rss_music_db_service_schemas.users.requests as db_user_requests

from rss_music_db_service.auth import errors, signup


users = APIRouter()


@users.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(request: Request):
    try:
        data = await request.json()
    except JSONDecodeError:
        response_data = {
            "code": 400,
            "error": ErrorType.INVALID_FORMAT,
            "message": "Expected a JSON body",
        }
        return JSONResponse(
            status_code=400,
            content=ErrorResponse().dump(response_data),
        )

    try:
        create_request = db_user_requests.CreateUserRequest().load(data)
    except ValidationError as error:
        message_lines = [
            f"{field}: {' + '.join(issues)}"
            for field, issues in error.messages_dict.items()
        ]
        response_data = {
            "code": 400,
            "error": ErrorType.INVALID_ARGUMENT,
            "message": "\n".join(message_lines),
        }
        return JSONResponse(
            status_code=400,
            content=ErrorResponse().dump(response_data),
        )

    try:
        signup.create_and_add_user(
            create_request["username"],
            create_request["email"],
            create_request["password"],
        )
    except errors.NotUniqueError as error:
        response_data = {
            "code": 409,
            "error": ErrorType.NOT_UNIQUE,
            "message": "The username or email has been used already",
            "details": {
                "field": error.field,
            },
        }
        return JSONResponse(
            status_code=409,
            content=ErrorResponse().dump(response_data),
        )

    return {
        "code": 201
    }

