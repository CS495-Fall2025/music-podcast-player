from marshmallow import Schema, fields


class OperationSuccessResponse(Schema):
    success = fields.Bool(required=True)
