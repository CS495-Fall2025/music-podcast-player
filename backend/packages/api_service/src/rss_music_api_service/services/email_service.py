from flask import current_app


class EmailDeliveryError(RuntimeError):
    def __init__(self, message: str):
        super().__init__(message)


def send_verification_code(email: str, code: str) -> None:
    subject = "Verify your account"
    body = (
        "Thanks for signing up. "
        f"Use this verification code to complete registration: {code}. "
        "This code expires in 15 minutes."
    )
    _send_email(email, subject, body)


def send_password_reset_code(email: str, code: str) -> None:
    subject = "Password reset code"
    body = (
        "We received a request to reset your password. "
        f"Use this code to continue: {code}. "
        "This code expires in 15 minutes."
    )
    _send_email(email, subject, body)


def _send_email(to_email: str, subject: str, body: str) -> None:
    source_email = current_app.config.get("SES_FROM_EMAIL")

    if not source_email:
        raise EmailDeliveryError("Missing SES_FROM_EMAIL configuration")

    try:
        import boto3

        client = boto3.client("sesv2")
        client.send_email(
            FromEmailAddress=source_email,
            Destination={"ToAddresses": [to_email]},
            Content={
                "Simple": {
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": body}},
                }
            },
        )
    except Exception as error:
        raise EmailDeliveryError("Failed to send email") from error
