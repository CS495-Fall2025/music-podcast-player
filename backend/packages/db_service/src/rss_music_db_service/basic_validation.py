from json import JSONDecodeError

from fastapi import Request
from fastapi.responses import JSONResponse
from marshmallow import Schema, ValidationError

from rss_music_db_service_schemas import ErrorResponse, ErrorType


async def validate_json(request: Request, schema: Schema) -> JSONResponse | dict:
    try:
        data = await request.json()
    except JSONDecodeError:
        response_data = {
            "code": 400,
            "error": ErrorType.INVALID_FORMAT,
            "message": "Expected a JSON body",
        }
        return JSONResponse(
            status_code=400,
            content=ErrorResponse().dump(response_data),
        )

    try:
        valid_request = schema.load(data)
    except ValidationError as error:
        message_lines = [
            f"{field}: {' + '.join(issues)}"
            for field, issues in error.messages_dict.items()
        ]
        response_data = {
            "code": 400,
            "error": ErrorType.INVALID_ARGUMENT,
            "message": "\n".join(message_lines),
            "details": error.messages_dict,
        }
        return JSONResponse(
            status_code=400,
            content=ErrorResponse().dump(response_data),
        )

    return valid_request
