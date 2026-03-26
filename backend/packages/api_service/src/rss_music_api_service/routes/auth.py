from functools import wraps
import flask
from datetime import datetime, timezone
from flask import Blueprint, request, session, current_app
from marshmallow import ValidationError

from rss_music_api_service.auth import signup, login, pkce, email_codes
from rss_music_api_service.auth.current_user import get_current_user_id
from rss_music_api_service.errors import RequestError, get_error_response
from rss_music_api_service.internal_apis import db_service
from rss_music_api_service.internal_apis import errors as db_errors
from rss_music_api_service.schemas import (
    SignUpRequestSchema,
    VerificationCodeRequestSchema,
    EmailCodeRequestSchema,
    EmailRequestSchema,
    ResetPasswordRequestSchema,
)
from rss_music_api_service.logging_config import log_request, get_logger
from rss_music_api_service.services import email_service

AUTH_BP = Blueprint("auth", __name__, url_prefix="/auth")
logger = get_logger(__name__)
PENDING_SIGNUP_KEY = "pending_signup"


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if get_current_user_id() is None:
            return {
                "code": 401,
                "error": "MissingToken",
                "message": "No token foudn",
            }, 401
        return func(*args, **kwargs)

    return wrapper


@AUTH_BP.after_request
def log_response(response):
    level = (
        "info"
        if response.status_code < 400
        else "warn"
        if response.status_code < 500
        else "error"
    )
    log_request(
        logger,
        level,
        "response_sent",
        "Sending response",
        user_id=get_current_user_id(),
        route=request.path,
        status_code=response.status_code,
    )
    return response


@AUTH_BP.post("/signup")
def post_signup() -> dict:
    log_request(
        logger,
        "info",
        "request_received",
        "Signup request received",
        user_id=get_current_user_id(),
        route="/auth/signup",
    )

    try:
        data = request.get_json(silent=True)

        if data is None:
            return get_error_response(RequestError.INVALID_FORMAT)

        valid_request = SignUpRequestSchema().load(data)
    except ValidationError:
        return get_error_response(RequestError.INVALID_ARGUMENT)

    verification_code = email_codes.generate_code()
    expires_at = email_codes.generate_expiration()

    session[PENDING_SIGNUP_KEY] = {
        "username": valid_request["username"],
        "email": valid_request["email"],
        "password": valid_request["password"],
        "code": verification_code,
        "expires_at": expires_at.isoformat(),
    }

    try:
        email_service.send_verification_code(valid_request["email"], verification_code)
    except email_service.EmailDeliveryError:
        return {
            "code": 502,
            "error": "EmailDeliveryFailed",
            "message": "Could not send verification email",
        }, 502

    return {
        "code": 201,
        "verification_required": True,
    }, 201


@AUTH_BP.post("/signup/verify")
def post_signup_verify() -> tuple:
    try:
        data = request.get_json(silent=True)

        if data is None:
            return get_error_response(RequestError.INVALID_FORMAT)

        valid_request = VerificationCodeRequestSchema().load(data)
    except ValidationError:
        return get_error_response(RequestError.INVALID_ARGUMENT)

    pending_signup = session.get(PENDING_SIGNUP_KEY)

    if pending_signup is None:
        return {
            "code": 400,
            "error": "InvalidSession",
            "message": "No pending signup found. Start signup again.",
        }, 400

    if pending_signup.get("code") != valid_request["code"]:
        return {
            "code": 400,
            "error": "InvalidVerificationCode",
            "message": "Invalid or expired verification code",
        }, 400

    expires_at_raw = pending_signup.get("expires_at")

    if not expires_at_raw:
        return {
            "code": 400,
            "error": "InvalidVerificationCode",
            "message": "Invalid or expired verification code",
        }, 400

    try:
        expires_at = datetime.fromisoformat(expires_at_raw)
    except ValueError:
        return {
            "code": 400,
            "error": "InvalidVerificationCode",
            "message": "Invalid or expired verification code",
        }, 400

    if expires_at < datetime.now(timezone.utc):
        return {
            "code": 400,
            "error": "InvalidVerificationCode",
            "message": "Invalid or expired verification code",
        }, 400

    try:
        signup.create_and_add_user(
            pending_signup["username"],
            pending_signup["email"],
            pending_signup["password"],
        )
    except db_errors.InternalAPIUniquenessError as error:
        return get_error_response(RequestError.VALUE_NOT_UNIQUE, {"field": error.field})
    except db_errors.InternalAPIBadResponseError:
        return get_error_response(RequestError.INTERNAL_API_BAD_RESPONSE)
    except db_errors.InternalAPITransportError:
        return get_error_response(RequestError.INTERNAL_API_TIMEOUT)

    session.pop(PENDING_SIGNUP_KEY, None)

    return {
        "code": 201,
        "verified": True,
        "account_created": True,
    }, 201


@AUTH_BP.get("/")
def get_auth() -> dict:
    """
    Start the authentication flow.
    Frontend will generate PKCE challenge and send it here.
    Backend stores the challenge in session for verification during login.
    """
    # Get the code challenge from query parameters
    code_challenge = request.args.get("code_challenge")

    if not code_challenge:
        return {
            "code": 400,
            "error": "MissingParameter",
            "message": "Missing code_challenge parameter",
        }, 400

    # Store challenge in session for later verification
    session["code_challenge"] = code_challenge

    return {
        "status": "ok",
    }, 200


@AUTH_BP.post("/login")
def post_login() -> tuple:
    """
    Authenticate user with username, password, and PKCE verifier.
    Returns JWT if successful.
    """
    log_request(
        logger,
        "info",
        "request_received",
        "Login request received",
        user_id=get_current_user_id(),
        route="/auth/login",
    )

    try:
        data = request.get_json(silent=True)

        if data is None:
            return get_error_response(RequestError.INVALID_FORMAT)

        username = data.get("username")
        password = data.get("password")
        code_verifier = data.get("code_verifier")

        if not username or not password or not code_verifier:
            return get_error_response(RequestError.INVALID_ARGUMENT)

    except Exception:
        return get_error_response(RequestError.INVALID_FORMAT)

    # Verify PKCE challenge
    stored_challenge = session.get("code_challenge")
    if not stored_challenge:
        return {
            "code": 400,
            "error": "InvalidSession",
            "message": "Invalid session: no PKCE challenge found",
        }, 400

    if not pkce.verify_code_challenge(code_verifier, stored_challenge):
        return {
            "code": 401,
            "error": "InvalidPKCE",
            "message": "Invalid PKCE verifier",
        }, 401

    try:
        user_id, username, email_verified = login.authenticate_user(username, password)
    except login.InvalidCredentialsError:
        return {
            "code": 401,
            "error": "InvalidCredentials",
            "message": "Invalid credentials",
        }, 401
    except db_errors.InternalAPIBadResponseError:
        return get_error_response(RequestError.INTERNAL_API_BAD_RESPONSE)
    except db_errors.InternalAPITransportError:
        return get_error_response(RequestError.INTERNAL_API_TIMEOUT)

    if not email_verified:
        log_request(
            logger,
            "warn",
            "response_sent",
            "Email not verified: login blocked",
            user_id=user_id,
            route="/auth/login",
            status_code=403,
        )
        return {
            "code": 403,
            "error": "EmailNotVerified",
            "message": "Email verification is required before signing in",
        }, 403

    secret_key = current_app.config.get("SECRET_KEY", "dev-secret-key")
    tokens = login.generate_tokens(user_id, username, secret_key)

    session.pop("code_challenge", None)
    session.pop("code_verifier_expected", None)

    is_production = current_app.config.get("SESSION_COOKIE_SECURE", True)

    response = flask.make_response({"success": True}, 200)

    response.set_cookie(
        "access_token",
        tokens["access_token"],
        httponly=True,
        secure=is_production,
        samesite="Lax",
        max_age=3600,
    )

    response.set_cookie(
        "refresh_token",
        tokens["refresh_token"],
        httponly=True,
        secure=is_production,
        samesite="Lax",
        max_age=604800,
    )

    return response


@AUTH_BP.post("/verify")
def post_verify() -> tuple:
    """
    Verify a JWT token from httpOnly cookie and check if the user still exists.
    Frontend calls this to validate tokens on app startup.
    """
    log_request(
        logger,
        "info",
        "request_received",
        "Token verification request received",
        user_id=get_current_user_id(),
        route="/auth/verify",
    )

    token = request.cookies.get("access_token")

    if not token:
        return {
            "valid": False,
            "code": 401,
            "error": "MissingToken",
            "message": "No token found",
        }, 401

    secret_key = current_app.config.get("SECRET_KEY")

    try:
        payload = login.verify_jwt(
            token, secret_key, expected_type=login.TokenType.ACCESS
        )
        user_id = payload.get("sub")

        # Verify user still exists in database
        if not db_service.check_user_exists(user_id):
            return {
                "valid": False,
                "code": 401,
                "error": "UserNotFound",
                "message": "User not found",
            }, 401

        user_info = {
            "id": payload.get("sub"),
            "username": payload.get("name"),
            "email": payload.get("email"),
        }

        return {"valid": True, "user": user_info}, 200
    except login.UserNotFoundError as e:
        return {
            "valid": False,
            "code": 401,
            "error": "UserNotFound",
            "message": str(e),
        }, 401
    except login.InvalidTokenError as e:
        return {
            "valid": False,
            "code": 401,
            "error": "InvalidToken",
            "message": str(e),
        }, 401
    except db_errors.InternalAPIBadResponseError:
        return get_error_response(RequestError.INTERNAL_API_BAD_RESPONSE)
    except db_errors.InternalAPITransportError:
        return get_error_response(RequestError.INTERNAL_API_TIMEOUT)


@AUTH_BP.post("/refresh")
def post_refresh() -> tuple:
    """
    Use a refresh token to get a new access token.
    This allows users to stay logged in without re-entering credentials.
    """
    log_request(
        logger,
        "info",
        "request_received",
        "Token refresh request received",
        user_id=get_current_user_id(),
        route="/auth/refresh",
    )

    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        return {
            "code": 401,
            "error": "MissingToken",
            "message": "No refresh token found",
        }, 401

    secret_key = current_app.config.get("SECRET_KEY")

    try:
        payload = login.verify_jwt(
            refresh_token, secret_key, expected_type=login.TokenType.REFRESH
        )
    except login.UserNotFoundError:
        return {"code": 401, "error": "UserNotFound", "message": "User not found"}, 401
    except login.InvalidTokenError as e:
        return {"code": 401, "error": "InvalidToken", "message": str(e)}, 401
    except db_errors.InternalAPIBadResponseError:
        return get_error_response(RequestError.INTERNAL_API_BAD_RESPONSE)
    except db_errors.InternalAPITransportError:
        return get_error_response(RequestError.INTERNAL_API_TIMEOUT)

    user_id = payload.get("sub")
    username = payload.get("name")

    new_access_token = login.generate_jwt(
        user_id,
        username,
        secret_key,
        expires_in_hours=1,
        token_type=login.TokenType.ACCESS,
    )

    is_production = current_app.config.get("SESSION_COOKIE_SECURE", True)

    response = flask.make_response({"success": True}, 200)

    response.set_cookie(
        "access_token",
        new_access_token,
        httponly=True,
        secure=is_production,
        samesite="Lax",
        max_age=3600,
    )

    return response


@AUTH_BP.post("/logout")
def post_logout() -> tuple:
    """
    Log out by clearing authentication cookies.
    """
    log_request(
        logger,
        "info",
        "request_received",
        "Logout request received",
        user_id=get_current_user_id(),
        route="/auth/logout",
    )

    response = flask.make_response({"success": True}, 200)
    response.set_cookie("access_token", "", httponly=True, max_age=0)
    response.set_cookie("refresh_token", "", httponly=True, max_age=0)

    return response


@AUTH_BP.post("/verify-email")
def post_verify_email() -> tuple:
    try:
        data = request.get_json(silent=True)

        if data is None:
            return get_error_response(RequestError.INVALID_FORMAT)

        valid_request = EmailCodeRequestSchema().load(data)
    except ValidationError:
        return get_error_response(RequestError.INVALID_ARGUMENT)

    try:
        success = db_service.verify_email(
            valid_request["email"],
            valid_request["code"],
        )
    except db_errors.InternalAPIBadResponseError:
        return get_error_response(RequestError.INTERNAL_API_BAD_RESPONSE)
    except db_errors.InternalAPITransportError:
        return get_error_response(RequestError.INTERNAL_API_TIMEOUT)

    if not success:
        return {
            "code": 400,
            "error": "InvalidVerificationCode",
            "message": "Invalid or expired verification code",
        }, 400

    return {"code": 200, "verified": True}, 200


@AUTH_BP.post("/resend-verification")
def post_resend_verification() -> tuple:
    try:
        data = request.get_json(silent=True)

        if data is None:
            return get_error_response(RequestError.INVALID_FORMAT)

        valid_request = EmailRequestSchema().load(data)
    except ValidationError:
        return get_error_response(RequestError.INVALID_ARGUMENT)

    code = email_codes.generate_code()
    expires_at = email_codes.generate_expiration()

    try:
        user_exists = db_service.set_email_verification_code(
            valid_request["email"], code, expires_at.isoformat()
        )

        if user_exists:
            email_service.send_verification_code(valid_request["email"], code)
    except db_errors.InternalAPIBadResponseError:
        return get_error_response(RequestError.INTERNAL_API_BAD_RESPONSE)
    except db_errors.InternalAPITransportError:
        return get_error_response(RequestError.INTERNAL_API_TIMEOUT)
    except email_service.EmailDeliveryError:
        return {
            "code": 502,
            "error": "EmailDeliveryFailed",
            "message": "Could not send verification email",
        }, 502

    return {"code": 200, "success": True}, 200


@AUTH_BP.post("/forgot-password")
def post_forgot_password() -> tuple:
    try:
        data = request.get_json(silent=True)

        if data is None:
            return get_error_response(RequestError.INVALID_FORMAT)

        valid_request = EmailRequestSchema().load(data)
    except ValidationError:
        return get_error_response(RequestError.INVALID_ARGUMENT)

    code = email_codes.generate_code()
    expires_at = email_codes.generate_expiration()

    try:
        user_exists = db_service.set_password_reset_code(
            valid_request["email"], code, expires_at.isoformat()
        )

        if user_exists:
            email_service.send_password_reset_code(valid_request["email"], code)
    except db_errors.InternalAPIBadResponseError:
        return get_error_response(RequestError.INTERNAL_API_BAD_RESPONSE)
    except db_errors.InternalAPITransportError:
        return get_error_response(RequestError.INTERNAL_API_TIMEOUT)
    except email_service.EmailDeliveryError:
        return {
            "code": 502,
            "error": "EmailDeliveryFailed",
            "message": "Could not send reset email",
        }, 502

    return {"code": 200, "success": True}, 200


@AUTH_BP.post("/reset-password")
def post_reset_password() -> tuple:
    try:
        data = request.get_json(silent=True)

        if data is None:
            return get_error_response(RequestError.INVALID_FORMAT)

        valid_request = ResetPasswordRequestSchema().load(data)
    except ValidationError:
        return get_error_response(RequestError.INVALID_ARGUMENT)

    try:
        password_was_reset = db_service.reset_password(
            valid_request["email"],
            valid_request["code"],
            valid_request["new_password"],
        )
    except db_errors.InternalAPIBadResponseError:
        return get_error_response(RequestError.INTERNAL_API_BAD_RESPONSE)
    except db_errors.InternalAPITransportError:
        return get_error_response(RequestError.INTERNAL_API_TIMEOUT)

    if not password_was_reset:
        return {
            "code": 400,
            "error": "InvalidResetCode",
            "message": "Invalid or expired reset code",
        }, 400

    return {"code": 200, "success": True}, 200
