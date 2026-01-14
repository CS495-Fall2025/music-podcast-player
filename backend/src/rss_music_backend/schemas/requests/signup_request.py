import re

from marshmallow import Schema, fields, validate

from rss_music_backend.database.users import USERNAME_MAX_LENGTH


class SignUpRequestSchema(Schema):
    username = fields.Str(
        required=True,
        validate=validate.length(min=6, max=USERNAME_MAX_LENGTH),
    )
    email = fields.Email(required=True),
    password = fields.Str(required=True, validate=validate.Length(min=8, max=64))
