from marshmallow import Schema, fields, validate

import rss_music_common_validators as common_validate


class UserLoginResponse(Schema):
    username = fields.Str(
        required=True,
        validate=common_validate.username,
    )
    id = fields.Int(required=True, validate=validate.Range(min=0))
    email_verified = fields.Bool(required=True)
    is_admin = fields.Bool(load_default=False)
