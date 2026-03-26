class InternalAPIError(RuntimeError):
    def __init__(self, message: str):
        super().__init__(message)


# Errors occuring while sending a request to an internal API
class InternalAPITransportError(InternalAPIError):
    def __init__(self, message: str):
        super().__init__(message)


class InternalAPITimeoutError(InternalAPITransportError):
    def __init__(self, message: str):
        super().__init__(message)


# Errors returned by an external API
class InternalAPIReturnedError(InternalAPIError):
    def __init__(self, message: str):
        super().__init__(message)


class InternalAPIBadResponseError(InternalAPIReturnedError):
    def __init__(self, message: str):
        super().__init__(message)


class InternalAPIUniquenessError(InternalAPIReturnedError):
    def __init__(self, message: str, field: str):
        super().__init__(message)
        self.field = field


# Errors encountered while parsing a successful response from an external API
class InternalAPIResponseError(InternalAPIError):
    def __init__(self, message: str):
        super().__init__(message)


class InternalAPIInvalidResponseFormatError(InternalAPIResponseError):
    def __init__(self, message: str):
        super().__init__(message)


class InternalAPIInvalidResponseDataError(InternalAPIResponseError):
    def __init__(self, message: str):
        super().__init__(message)


class InternalAPINotFoundError(InternalAPIReturnedError):
    def __init__(self, message: str):
        super().__init__(message)
