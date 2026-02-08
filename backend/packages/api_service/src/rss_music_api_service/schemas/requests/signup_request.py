import re

from marshmallow import Schema, fields, validate

from rss_music_api_service.database.users import USERNAME_MAX_LENGTH
from rss_music_api_service.schemas import SAnd


class SignUpRequestSchema(Schema):
    username = fields.Str(
        required=True,
        validate=SAnd(
            validate.Length(min=6, max=USERNAME_MAX_LENGTH),
            validate.Regexp(r"^[a-zA-Z0-9]\w*[a-zA-Z0-9]$", flags=re.UNICODE),
        ),
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=SAnd(
            validate.Length(min=12, max=64),
            # Require at least one alphabetical character, digit, and special character.
            validate.Regexp(
                r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).*$",
                flags=re.UNICODE,
            ),
        ),
    )
