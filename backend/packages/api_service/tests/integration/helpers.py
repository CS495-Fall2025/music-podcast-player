import json

from requests import Response


def make_response(json_data: dict | None, status_code: int) -> Response:
    response = Response()
    response.status_code = 200

    if json_data is not None:
        sdata = json.dumps(json_data)
        response._content = sdata.encode("UTF-8")
        response.headers = {"Content-Type": "application/json"}

    return response
