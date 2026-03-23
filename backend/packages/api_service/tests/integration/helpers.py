import json

from requests import Response


class ConstantResponse:
    def __init__(self, status_code: int, json_data: dict | None):
        self.status_code = status_code
        self.json_data = json_data

    def to_response(self) -> Response:
        return make_response(self.json_data, self.status_code)


def make_response(json_data: dict | None, status_code: int) -> Response:
    response = Response()
    response.status_code = status_code

    if json_data is not None:
        sdata = json.dumps(json_data)
        response._content = sdata.encode("UTF-8")
        response.headers = {"Content-Type": "application/json"}

    return response
