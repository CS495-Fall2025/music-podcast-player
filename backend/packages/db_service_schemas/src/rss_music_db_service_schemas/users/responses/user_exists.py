from marshmallow import Schema, fields, validate


class UserExistsResponse(Schema):
    code = fields.Int(required=True, validate=validate.Range(min=200, max=200))
    exists = fields.Bool(required=True)
