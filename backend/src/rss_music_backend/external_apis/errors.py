from enum import Enum, auto


class ExternalError(Enum):
    TIMEOUT = auto()
    BAD_REQUEST = auto()
    BAD_AUTHORIZATION = auto()
