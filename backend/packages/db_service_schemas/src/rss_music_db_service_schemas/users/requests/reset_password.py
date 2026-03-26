from marshmallow import Schema, fields, validate

import rss_music_common_validators as common_validate


class ResetPasswordRequest(Schema):
    email = fields.Email(required=True)
    code = fields.Str(required=True, validate=validate.Regexp(r"^\d{6}$"))
    new_password = fields.Str(required=True, validate=common_validate.password)
