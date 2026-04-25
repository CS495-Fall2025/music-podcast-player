import pytest
from sqlalchemy.orm import Session

import rss_music_data_model as data_model
from rss_music_set_admin import UserNotFoundError, set_admin


@pytest.fixture
def session() -> Session:
    data_model.initialize_engine("sqlite:///:memory:")

    engine = data_model.get_engine()
    data_model.Base.metadata.create_all(engine)

    with data_model.make_session() as session:
        yield session


def test_throws_error_when_neither_email_nor_username(session: Session) -> None:
    with pytest.raises(ValueError):
        set_admin(session, True)


def test_throws_error_when_email_not_found(session: Session) -> None:
    with pytest.raises(UserNotFoundError):
        set_admin(session, True, email="nonexistant@domain.com")


def test_throws_error_when_username_not_found(session: Session) -> None:
    with pytest.raises(UserNotFoundError):
        set_admin(session, True, username="nonexistant")


def test_promotes_user_by_email(session: Session) -> None:
    user = data_model.User(
        username="username",
        email="email@domain.com",
        password=b"password-hash",
        is_admin=False,
    )

    session.add(user)
    session.commit()

    set_admin(session, True, email=user.email)

    assert user.is_admin


def test_promotes_user_by_username(session: Session) -> None:
    user = data_model.User(
        username="username",
        email="email@domain.com",
        password=b"password-hash",
        is_admin=False,
    )

    session.add(user)
    session.commit()

    set_admin(session, True, username=user.username)

    assert user.is_admin


def test_demotes_user(session: Session) -> None:
    user = data_model.User(
        username="username",
        email="email@domain.com",
        password=b"password-hash",
        is_admin=True,
    )

    session.add(user)
    session.commit()

    set_admin(session, False, email=user.email)

    assert not user.is_admin
