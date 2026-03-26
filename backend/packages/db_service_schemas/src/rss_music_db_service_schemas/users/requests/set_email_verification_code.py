from marshmallow import Schema, fields, validate


class SetEmailVerificationCodeRequest(Schema):
    email = fields.Email(required=True)
    code = fields.Str(required=True, validate=validate.Regexp(r"^\d{6}$"))
    expires_at = fields.DateTime(required=True)
