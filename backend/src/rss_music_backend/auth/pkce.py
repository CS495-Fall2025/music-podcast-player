import hashlib
import base64
import secrets


def generate_code_verifier(length: int = 128) -> str:
    """
    Generate a PKCE code verifier.

    Returns:
        A URL-safe base64-encoded random string
    """
    if not (43 <= length <= 128):
        raise ValueError("Code verifier length must be between 43 and 128")

    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(length)).decode(
        "utf-8"
    )
    return code_verifier.rstrip("=")


def generate_code_challenge(code_verifier: str) -> str:
    """
    Generate a PKCE code challenge from a code verifier using S256 method.
    """
    code_sha = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_sha).decode("utf-8")
    return code_challenge.rstrip("=")


def verify_code_challenge(code_verifier: str, code_challenge: str) -> bool:
    """
    Verify that a code verifier matches a code challenge.

    Args:
        code_verifier: The verifier provided by the client
        code_challenge: The challenge stored on the server

    Returns:
        True if the verifier matches the challenge, False otherwise
    """
    computed_challenge = generate_code_challenge(code_verifier)
    return computed_challenge == code_challenge
