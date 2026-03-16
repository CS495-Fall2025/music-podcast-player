class NotUniqueError(ValueError):
    def __init__(self, field: str):
        super().__init__(f"{field} was not unique")
        self.field = field


class UserNotFoundError(Exception):
    """Raised when the provided user_id does not exist in the database"""
    pass
