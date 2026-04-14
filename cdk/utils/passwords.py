import base64
import secrets

# Around 64 base64 chars.
DB_SECRET_LENGTH = 48


# Generates a database secret to use with our RDS instance.
def generate_db_secret() -> str:
    password_bytes = secrets.token_bytes(DB_SECRET_LENGTH)
    password = base64.urlsafe_b64encode(password_bytes).decode("UTF-8")
    return password

