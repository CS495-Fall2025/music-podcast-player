from fastapi import status, APIRouter, Request
from fastapi.responses import JSONResponse

from rss_music_db_service_schemas import ErrorResponse, ErrorType
import rss_music_db_service_schemas.users.requests as db_user_requests
import rss_music_db_service_schemas.users.responses as db_user_responses

from rss_music_db_service import errors
from rss_music_db_service.users import create, exists, login
from rss_music_db_service.basic_validation import validate_json


users = APIRouter()


@users.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(request: Request):
    result = await validate_json(request, db_user_requests.CreateUserRequest())

    if isinstance(result, JSONResponse):
        return result

    try:
        create.create_and_add_user(
            result["username"],
            result["email"],
            result["password"],
        )
    except errors.NotUniqueError as error:
        response_data = {
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

    response_data = {
        "username": result["username"],
    }
    return db_user_responses.CreateUserResponse().dump(response_data)


@users.post("/exists")
async def user_exists(request: Request):
    result = await validate_json(request, db_user_requests.UserExistsRequest())

    if isinstance(result, JSONResponse):
        return result

    found_flag = False
    for field in result.keys():
        match field:
            case "username":
                if exists.user_exists_by_username(result["username"]):
                    found_flag = True
                    # breaks refer to the for loop, not the match.
                    break
            case "email":
                if exists.user_exists_by_email(result["email"]):
                    found_flag = True
                    break
            case "id":
                if exists.user_exists_by_id(result["id"]):
                    found_flag = True
                    break

    response_data = {
        "exists": found_flag,
    }
    return db_user_responses.UserExistsResponse().dump(response_data)


@users.post("/login")
async def user_login(request: Request):
    result = await validate_json(request, db_user_requests.UserLoginRequest())

    if isinstance(result, JSONResponse):
        return result
    
    user = login.authenticate_user(result["username"], result["password"])

    if user is None:
        response_data = {
            "error": ErrorType.INVALID_CREDENTIALS,
            "message": "The provided credentials are invalid",
        }

        return JSONResponse(
            status_code=401,
            content=ErrorResponse().dump(response_data)
        )

    response_data = {
        "username": user.username,
        "id": user.id,
    }
    return db_user_responses.UserLoginResponse().dump(response_data)
