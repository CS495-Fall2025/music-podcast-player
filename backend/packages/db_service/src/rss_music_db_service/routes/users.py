from fastapi import status, APIRouter, Request, Response
from fastapi.responses import JSONResponse

from rss_music_db_service_schemas import ErrorResponse, ErrorType
import rss_music_db_service_schemas.users.requests as db_user_requests
import rss_music_db_service_schemas.users.responses as db_user_responses

from rss_music_db_service import errors
from rss_music_db_service.users import (
    create,
    delete,
    exists,
    login,
    verification,
    password_reset,
    privacy,
)
from rss_music_db_service.basic_validation import validate_json
from rss_music_db_service.logging_config import log_request, get_logger


users = APIRouter()
logger = get_logger(__name__)


@users.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(request: Request, response: Response):
    log_request(
        logger,
        "info",
        "request_received",
        "Create user request received",
        route="/users/create",
    )

    result = await validate_json(request, db_user_requests.CreateUserRequest())

    if isinstance(result, JSONResponse):
        response.status_code = result.status_code
        level = "warn" if result.status_code < 500 else "error"
        log_request(
            logger,
            level,
            "response_sent",
            "Response sent",
            route="/users/create",
            status_code=result.status_code,
        )
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
        response.status_code = 409
        log_request(
            logger,
            "warn",
            "response_sent",
            "Response sent",
            route="/users/create",
            status_code=409,
        )
        return JSONResponse(
            status_code=409,
            content=ErrorResponse().dump(response_data),
        )

    response_data = {
        "username": result["username"],
    }

    log_request(
        logger,
        "info",
        "response_sent",
        "Response sent",
        route="/users/create",
        status_code=201,
    )

    return db_user_responses.CreateUserResponse().dump(response_data)


@users.post("/exists")
async def user_exists(request: Request, response: Response):
    log_request(
        logger,
        "info",
        "request_received",
        "User exists request received",
        route="/users/exists",
    )

    result = await validate_json(request, db_user_requests.UserExistsRequest())

    if isinstance(result, JSONResponse):
        response.status_code = result.status_code
        level = "warn" if result.status_code < 500 else "error"
        log_request(
            logger,
            level,
            "response_sent",
            "Response sent",
            route="/users/exists",
            status_code=result.status_code,
        )
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

    log_request(
        logger,
        "info",
        "response_sent",
        "Response sent",
        route="/users/exists",
        status_code=200,
    )

    return db_user_responses.UserExistsResponse().dump(response_data)


@users.post("/login")
async def user_login(request: Request, response: Response):
    log_request(
        logger,
        "info",
        "request_received",
        "User login request received",
        route="/users/login",
    )

    result = await validate_json(request, db_user_requests.UserLoginRequest())

    if isinstance(result, JSONResponse):
        response.status_code = result.status_code
        level = "warn" if result.status_code < 500 else "error"
        log_request(
            logger,
            level,
            "response_sent",
            "Response sent",
            route="/users/login",
            status_code=result.status_code,
        )
        return result

    user = login.authenticate_user(result["username"], result["password"])

    if user is None:
        response_data = {
            "error": ErrorType.INVALID_CREDENTIALS,
            "message": "The provided credentials are invalid",
        }

        response.status_code = 401
        log_request(
            logger,
            "warn",
            "response_sent",
            "Response sent",
            route="/users/login",
            status_code=401,
        )

        return JSONResponse(
            status_code=401, content=ErrorResponse().dump(response_data)
        )

    response_data = {
        "username": user.username,
        "id": user.id,
        "email_verified": user.email_verified,
        "is_admin": user.is_admin,
    }

    log_request(
        logger,
        "info",
        "response_sent",
        "Response sent",
        route="/users/login",
        status_code=200,
    )

    return db_user_responses.UserLoginResponse().dump(response_data)


@users.post("/set-email-verification-code")
async def set_email_verification_code(request: Request, response: Response):
    log_request(
        logger,
        "info",
        "request_received",
        "Set email verification code request received",
        route="/users/set-email-verification-code",
    )

    result = await validate_json(
        request, db_user_requests.SetEmailVerificationCodeRequest()
    )

    if isinstance(result, JSONResponse):
        response.status_code = result.status_code
        level = "warn" if result.status_code < 500 else "error"
        log_request(
            logger,
            level,
            "response_sent",
            "Response sent",
            route="/users/set-email-verification-code",
            status_code=result.status_code,
        )
        return result

    updated = verification.set_email_verification_code(
        result["email"],
        result["code"],
        result["expires_at"],
    )

    response_data = {"success": updated}

    log_request(
        logger,
        "info",
        "response_sent",
        "Response sent",
        route="/users/set-email-verification-code",
        status_code=200,
    )

    return db_user_responses.OperationSuccessResponse().dump(response_data)


@users.delete("/{user_id}")
async def delete_user(user_id: int):
    log_request(
        logger,
        "info",
        "request_received",
        "Delete user request received",
        route=f"/users/{user_id}",
    )

    deleted = delete.delete_user(user_id)

    if not deleted:
        log_request(
            logger,
            "warn",
            "response_sent",
            "Response sent",
            route=f"/users/{user_id}",
            status_code=404,
        )
        return JSONResponse(
            status_code=404,
            content=ErrorResponse().dump(
                {
                    "error": ErrorType.NOT_FOUND,
                    "message": "User was not found",
                }
            ),
        )

    log_request(
        logger,
        "info",
        "response_sent",
        "Response sent",
        route=f"/users/{user_id}",
        status_code=200,
    )

    return db_user_responses.OperationSuccessResponse().dump({"success": True})


@users.post("/verify-email")
async def verify_email(request: Request, response: Response):
    log_request(
        logger,
        "info",
        "request_received",
        "Verify email request received",
        route="/users/verify-email",
    )

    result = await validate_json(request, db_user_requests.VerifyEmailRequest())

    if isinstance(result, JSONResponse):
        response.status_code = result.status_code
        level = "warn" if result.status_code < 500 else "error"
        log_request(
            logger,
            level,
            "response_sent",
            "Response sent",
            route="/users/verify-email",
            status_code=result.status_code,
        )
        return result

    verified = verification.verify_email(result["email"], result["code"])

    response_data = {"success": verified}

    log_request(
        logger,
        "info",
        "response_sent",
        "Response sent",
        route="/users/verify-email",
        status_code=200,
    )

    return db_user_responses.OperationSuccessResponse().dump(response_data)


@users.post("/set-password-reset-code")
async def set_password_reset_code(request: Request, response: Response):
    log_request(
        logger,
        "info",
        "request_received",
        "Set password reset code request received",
        route="/users/set-password-reset-code",
    )

    result = await validate_json(
        request, db_user_requests.SetPasswordResetCodeRequest()
    )

    if isinstance(result, JSONResponse):
        response.status_code = result.status_code
        level = "warn" if result.status_code < 500 else "error"
        log_request(
            logger,
            level,
            "response_sent",
            "Response sent",
            route="/users/set-password-reset-code",
            status_code=result.status_code,
        )
        return result

    updated = password_reset.set_password_reset_code(
        result["email"],
        result["code"],
        result["expires_at"],
    )

    response_data = {"success": updated}

    log_request(
        logger,
        "info",
        "response_sent",
        "Response sent",
        route="/users/set-password-reset-code",
        status_code=200,
    )

    return db_user_responses.OperationSuccessResponse().dump(response_data)


@users.post("/reset-password")
async def reset_user_password(request: Request, response: Response):
    log_request(
        logger,
        "info",
        "request_received",
        "Reset password request received",
        route="/users/reset-password",
    )

    result = await validate_json(request, db_user_requests.ResetPasswordRequest())

    if isinstance(result, JSONResponse):
        response.status_code = result.status_code
        level = "warn" if result.status_code < 500 else "error"
        log_request(
            logger,
            level,
            "response_sent",
            "Response sent",
            route="/users/reset-password",
            status_code=result.status_code,
        )
        return result

    password_was_reset = password_reset.reset_password(
        result["email"], result["code"], result["new_password"]
    )

    response_data = {"success": password_was_reset}

    log_request(
        logger,
        "info",
        "response_sent",
        "Response sent",
        route="/users/reset-password",
        status_code=200,
    )

    return db_user_responses.OperationSuccessResponse().dump(response_data)


@users.get("/{user_id}/privacy")
async def get_user_privacy(user_id: int):
    log_request(
        logger,
        "info",
        "request_received",
        "Get user privacy request received",
        route=f"/users/{user_id}/privacy",
    )
    profile_public = privacy.get_profile_public(user_id)
    log_request(
        logger,
        "info",
        "response_sent",
        "Response sent",
        route=f"/users/{user_id}/privacy",
        status_code=200,
    )
    return {"profile_public": profile_public}


@users.patch("/{user_id}/privacy")
async def update_user_privacy(user_id: int, request: Request):
    log_request(
        logger,
        "info",
        "request_received",
        "Update user privacy request received",
        route=f"/users/{user_id}/privacy",
    )
    body = await request.json()
    profile_public = body.get("profile_public")
    if not isinstance(profile_public, bool):
        log_request(
            logger,
            "warn",
            "response_sent",
            "Response sent",
            route=f"/users/{user_id}/privacy",
            status_code=400,
        )
        return JSONResponse(
            status_code=400,
            content={
                "error": "InvalidArgument",
                "message": "profile_public must be a boolean",
            },
        )
    privacy.set_profile_public(user_id, profile_public)
    log_request(
        logger,
        "info",
        "response_sent",
        "Response sent",
        route=f"/users/{user_id}/privacy",
        status_code=200,
    )
    return {"profile_public": profile_public}
