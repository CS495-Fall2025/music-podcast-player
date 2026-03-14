from datetime import datetime, timedelta, timezone

from rss_music_data_model import User


def test_set_email_verification_code_success(client, db_session) -> None:
    user = User(
        username="testuser",
        email="testuser@domain.com",
        password=b"test-password-hash",
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/users/set-email-verification-code",
        json={
            "email": "testuser@domain.com",
            "code": "123456",
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat(),
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_verify_email_success(client, db_session) -> None:
    user = User(
        username="testuser",
        email="testuser@domain.com",
        password=b"test-password-hash",
        email_verification_code="123456",
        email_verification_code_expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=15),
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/users/verify-email",
        json={
            "email": "testuser@domain.com",
            "code": "123456",
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_reset_password_success(client, db_session) -> None:
    user = User(
        username="testuser",
        email="testuser@domain.com",
        password=b"test-password-hash",
        password_reset_code="123456",
        password_reset_code_expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=15),
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/users/reset-password",
        json={
            "email": "testuser@domain.com",
            "code": "123456",
            "new_password": "Password123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
