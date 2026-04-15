from typing import Callable


auth: Callable | None = None


def set_auth(new_auth: Callable) -> None:
    global auth
    auth = new_auth


def get_auth() -> Callable | None:
    return auth
