from rss_music_api_service.internal_apis import db_service


def create_and_add_user(username: str, email: str, password: str) -> None:
    db_service.create_user(username, email, password)
