from flask import Blueprint, request, session
from marshmallow import ValidationError
import os

from rss_music_backend.auth import errors, signup, login, pkce
from rss_music_backend.errors import RequestError, get_error_response
from rss_music_backend.schemas import SignUpRequestSchema

# All routes added to this BP are under "/auth"
AUTH_BP = Blueprint("auth", __name__, url_prefix="/auth")


@AUTH_BP.post("/signup")
def post_signup() -> dict:
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
    except errors.NotUniqueError as error:
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
        return {"error": "Missing code_challenge parameter"}, 400
    
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
    try:
        data = request.get_json(silent=True)
        
        if data is None:
            return get_error_response(RequestError.INVALID_FORMAT), 400
        
        username = data.get("username")
        password = data.get("password")
        code_verifier = data.get("code_verifier")
        
        if not username or not password or not code_verifier:
            return get_error_response(RequestError.INVALID_ARGUMENT), 400
        
    except Exception:
        return get_error_response(RequestError.INVALID_FORMAT), 400
    
    # Verify PKCE challenge
    stored_challenge = session.get("code_challenge")
    if not stored_challenge:
        return {"error": "Invalid session: no PKCE challenge found"}, 400
    
    if not pkce.verify_code_challenge(code_verifier, stored_challenge):
        return {"error": "Invalid PKCE verifier"}, 401
    
    # Authenticate user
    try:
        user = login.authenticate_user(username, password)
    except login.InvalidCredentialsError:
        return {"error": "Invalid credentials"}, 401
    
    # Generate JWT
    secret_key = os.getenv("RSS_PLAYER_SECRET_KEY", "dev-secret-key")
    token = login.generate_jwt(user, secret_key)
    
    # Clear session state
    session.pop("code_challenge", None)
    session.pop("code_verifier_expected", None)
    
    return {
        "token": token,
    }, 200


@AUTH_BP.post("/verify")
def post_verify() -> tuple:
    """
    Verify a JWT token and check if the user still exists.
    Frontend calls this to validate stored tokens on app startup.
    """
    try:
        data = request.get_json(silent=True)
        
        if data is None:
            return {"error": "Invalid request"}, 400
        
        token = data.get("token")
        if not token:
            return {"error": "Missing token"}, 400
        
    except Exception:
        return {"error": "Invalid request"}, 400
    
    secret_key = os.getenv("RSS_PLAYER_SECRET_KEY", "dev-secret-key")
    
    try:
        payload = login.verify_jwt(token, secret_key)
        return {
            "valid": True,
            "user": {
                "id": payload.get("sub"),
                "username": payload.get("name"),
                "email": payload.get("email"),
            }
        }, 200
    except login.InvalidTokenError as e:
        return {"valid": False, "error": str(e)}, 401