from enum import Enum

from marshmallow import Schema, fields, validate


class ErrorType(Enum):
    # Invalid or missing JSON.
    INVALID_FORMAT = "InvalidFormat"
    # Doesn't match expected schema.
    INVALID_ARGUMENT = "InvalidArgument"


class ErrorResponse(Schema):
    code = fields.Int(validate=validate.Range(min=400, max=599))
    error = fields.Enum(ErrorType, by_value=True, required=True)
    message = fields.Str(required=True)
