import hashlib
import os

from database import User, make_session


def attempt_signup_user(username: str, email: str, password: str) -> None:
    try:
        with make_session() as session:
            salt = os.urandom(16)
            # scrypt is recommended over bcrypt to prevent attacks from specialized
            # hardware
            hashed_password = hashlib.scrypt(
                password.encode("utf-8"),
                salt=salt, n=16384, r=8, p=1, dklen=60
            )
            user = User(username=username, email=email, password=hashed_password)
