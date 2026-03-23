from marshmallow import Schema, fields, validate

from rss_music_common_validators import username, password


class LoginRequestSchema(Schema):
    username = fields.Str(
        required=True,
        validate=username,
    )
    password = fields.Str(
        required=True,
        validate=password,
    )
    code_verifier = fields.Str(required=True, validate=validate.Length(min=1, max=256))
