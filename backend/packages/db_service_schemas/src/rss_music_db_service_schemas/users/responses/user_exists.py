from marshmallow import Schema, fields


class UserExistsResponse(Schema):
    exists = fields.Bool(required=True)
