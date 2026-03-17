class NotUniqueError(ValueError):
    def __init__(self, field: str):
        super().__init__(f"{field} was not unique")
        self.field = field


class UserNotFoundError(Exception):
    pass
