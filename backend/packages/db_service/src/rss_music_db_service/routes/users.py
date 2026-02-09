from fastapi import status, APIRouter, Request
from fastapi.responses import JSONResponse

from rss_music_db_service_schemas import ErrorResponse, ErrorType
import rss_music_db_service_schemas.users.requests as db_user_requests

from rss_music_db_service.auth import errors, signup
from rss_music_db_service.basic_validation import validate_json


users = APIRouter()


@users.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(request: Request):
    result = await validate_json(request, db_user_requests.CreateUserRequest())

    if isinstance(result, JSONResponse):
        return result

    try:
        signup.create_and_add_user(
            result["username"],
            result["email"],
            result["password"],
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

#@users.post("/create")
#async def user_exists(request: Request):
