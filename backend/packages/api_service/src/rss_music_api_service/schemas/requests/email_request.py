from marshmallow import Schema, fields


class EmailRequestSchema(Schema):
    email = fields.Email(required=True)
