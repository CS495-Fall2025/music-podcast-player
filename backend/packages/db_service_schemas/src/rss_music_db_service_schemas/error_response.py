from enum import Enum

from marshmallow import Schema, fields


class ErrorType(Enum):
    # Invalid or missing JSON.
    INVALID_FORMAT = "InvalidFormat"
    # Doesn't match expected schema.
    INVALID_ARGUMENT = "InvalidArgument"
    # An object argument that must be unique was not unique.
    NOT_UNIQUE = "NotUnique"
    # Credentials were invalid
    INVALID_CREDENTIALS = "InvalidCredentials"
    # Requested item was not found
    NOT_FOUND = "NotFound"


class ErrorResponse(Schema):
    error = fields.Enum(ErrorType, by_value=True, required=True)
    message = fields.Str(required=True)
    details = fields.Dict(keys=fields.Str())
