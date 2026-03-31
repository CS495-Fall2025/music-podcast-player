from marshmallow import Schema, fields, validate


class VerifyEmailRequest(Schema):
    email = fields.Email(required=True)
    code = fields.Str(required=True, validate=validate.Regexp(r"^\d{6}$"))
