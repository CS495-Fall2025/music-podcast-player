from marshmallow import Schema, fields, validate


import rss_music_common_validators as common_validate


class AuthenticateUserRequest(Schema):
    username = fields.Str(
        required=True,
        validate=common_validate.username,
    )
    password = fields.Str(
        required=True,
        validate=common_validate.password,
    )
