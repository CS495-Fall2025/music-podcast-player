from marshmallow import Schema, fields, validate


class UserExistsResponse(Schema):
    exists = fields.Bool(required=True)
