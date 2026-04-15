class ExternalAPIError(RuntimeError):
    def __init__(self, message: str):
        super().__init__(message)


# Errors occuring while sending a request to an external API
class ExternalAPITransportError(ExternalAPIError):
    def __init__(self, message: str):
        super().__init__(message)


class ExternalAPITimeoutError(ExternalAPITransportError):
    def __init__(self, message: str):
        super().__init__(message)


# Errors returned by an external API
class ExternalAPIReturnedError(ExternalAPIError):
    def __init__(self, message: str):
        super().__init__(message)


class ExternalAPIBadRequestError(ExternalAPIReturnedError):
    def __init__(self, message: str):
        super().__init__(message)


class ExternalAPIBadAuthenticationError(ExternalAPIReturnedError):
    def __init__(self, message: str):
        super().__init__(message)


class ExternalAPITooManyRequestsError(ExternalAPIReturnedError):
    def __init__(self, message: str):
        super().__init__(message)


# Errors encountered while parsing a successful response from an external API
class ExternalAPIResponseError(ExternalAPIError):
    def __init__(self, message: str):
        super().__init__(message)


class ExternalAPIInvalidResponseFormatError(ExternalAPIResponseError):
    def __init__(self, message: str):
        super().__init__(message)


class ExternalAPIInvalidResponseDataError(ExternalAPIResponseError):
    def __init__(self, message: str):
        super().__init__(message)
