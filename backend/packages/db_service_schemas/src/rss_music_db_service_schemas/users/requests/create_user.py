from marshmallow import Schema, fields

import rss_music_common_validators as common_validate


class CreateUserRequest(Schema):
    username = fields.Str(
        required=True,
        validate=common_validate.username,
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=common_validate.password,
    )
