from marshmallow import Schema, fields

import rss_music_common_validators as common_validate


class CreateUserResponse(Schema):
    username = fields.Str(
        required=True,
        validate=common_validate.username,
    )
