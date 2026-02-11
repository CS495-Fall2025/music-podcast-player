import flask
from flask import Blueprint, request, session, current_app
from marshmallow import ValidationError

from rss_music_api_service.auth import signup, login, pkce
from rss_music_api_service.auth.current_user import get_current_user_id
from rss_music_api_service.errors import RequestError, get_error_response
from rss_music_api_service.internal_apis import db_service 
from rss_music_api_service.internal_apis import errors as db_errors
from rss_music_api_service.schemas import SignUpRequestSchema
from rss_music_api_service.logging_config import log_request, get_logger

AUTH_BP = Blueprint("auth", __name__, url_prefix="/auth")
logger = get_logger(__name__)


@AUTH_BP.after_request
def log_response(response):
    level = "info" if response.status_code < 400 else "warn" if response.status_code < 500 else "error"
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

    try:
        signup.create_and_add_user(
            valid_request["username"],
            valid_request["email"],
            valid_request["password"],
        )
    except db_errors.InternalAPIUniquenessError as error:
        return get_error_response(RequestError.VALUE_NOT_UNIQUE, {"field": error.field})

    return {
        "code": 201,
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
        user_id, username = login.authenticate_user(username, password)
    except login.InvalidCredentialsError:
        return {
            "code": 401,
            "error": "InvalidCredentials",
            "message": "Invalid credentials",
        }, 401

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
        payload = login.verify_jwt(token, secret_key, expected_type=login.TokenType.ACCESS)
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
        payload = login.verify_jwt(refresh_token, secret_key, expected_type=login.TokenType.REFRESH)
    except login.UserNotFoundError:
        return {"code": 401, "error": "UserNotFound", "message": "User not found"}, 401
    except login.InvalidTokenError as e:
        return {"code": 401, "error": "InvalidToken", "message": str(e)}, 401

    user_id = payload.get("sub")
    username = payload.get("name")

    if not db_service.check_user_exists(user_id):
        return {
            "code": 401,
            "error": "UserNotFound",
            "message": "User not found",
        }, 401


    new_access_token = login.generate_jwt(
        user_id, username, secret_key, expires_in_hours=1, token_type=login.TokenType.ACCESS
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
