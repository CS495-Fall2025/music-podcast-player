from rss_music_data_model import User


def test_delete_user_route_not_found(client, db_session) -> None:
    """DELETE /users/{user_id} returns 404 if user doesn't exist."""
    response = client.delete("/users/999")

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "NotFound"


def test_delete_user_route_success(client, db_session) -> None:
    """DELETE /users/{user_id} successfully deletes user and returns 200."""
    user = User(
        username="delete_me",
        email="delete_me@domain.com",
        password=b"test-password-hash",
    )
    db_session.add(user)
    db_session.commit()

    response = client.delete(f"/users/{user.id}")

    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True


def test_delete_user_requires_valid_id(client) -> None:
    """DELETE /users/{user_id} with invalid ID format returns error."""
    response = client.delete("/users/invalid")

    # FastAPI path param validation error.
    assert response.status_code == 422
