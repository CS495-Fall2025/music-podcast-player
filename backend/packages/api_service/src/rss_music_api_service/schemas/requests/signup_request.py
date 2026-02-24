from marshmallow import Schema, fields

from rss_music_common_validators import username, password


class SignUpRequestSchema(Schema):
    username = fields.Str(
        required=True,
        validate=username,
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=password,
    )
