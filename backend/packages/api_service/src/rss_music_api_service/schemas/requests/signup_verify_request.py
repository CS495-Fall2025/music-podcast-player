from marshmallow import Schema, fields, validate

from rss_music_common_validators import username, password


class SignUpVerifyRequestSchema(Schema):
    username = fields.Str(required=True, validate=username)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=password)
    code = fields.Str(required=True, validate=validate.Regexp(r"^\d{6}$"))
