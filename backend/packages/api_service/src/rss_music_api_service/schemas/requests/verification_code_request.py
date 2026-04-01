from marshmallow import Schema, fields, validate


class VerificationCodeRequestSchema(Schema):
    code = fields.Str(required=True, validate=validate.Regexp(r"^\d{6}$"))
