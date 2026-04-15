from marshmallow import Schema, fields, validate

from rss_music_common_validators import password


class ResetPasswordRequestSchema(Schema):
    email = fields.Email(required=True)
    code = fields.Str(required=True, validate=validate.Regexp(r"^\d{6}$"))
    new_password = fields.Str(required=True, validate=password)
