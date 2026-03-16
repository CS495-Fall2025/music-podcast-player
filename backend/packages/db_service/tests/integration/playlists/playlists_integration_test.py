import pytest
from rss_music_data_model import User, Playlist


def test_create_playlist_integration(client, db_session):
    """
    Tests the full flow: API -> DB -> Response
    Covers the 'missing description' and 'int vs string' bugs.
    """
    # 1. Seed a user into the in-memory DB
    test_user = User(username="johndoe",
                     email="john@example.com", password=b"password123")
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    # 2. Call the API (POST)
    # Note: We include the user_id in the payload for now
    # (or via headers if your app uses get_current_user_id)
    payload = {
        "title": "My First Playlist",
        "created_by_user_id": test_user.id
        # description is omitted to verify the 'None' bug is fixed
    }

    response = client.post("/playlists/create", json=payload)

    # 3. Assertions
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My First Playlist"
    assert data["created_by_user_id"] == test_user.id

    # 4. Verify DB State: Did it actually save?
    db_playlist = db_session.query(Playlist).filter_by(
        title="My First Playlist").first()
    assert db_playlist is not None
    assert db_playlist.created_by_user_id == test_user.id


def test_get_playlists_me_integration(client, db_session):
    """
    Tests the 'Get Playlists' flow and ensures we handle non-existent users with 404.
    """
    # 1. Create a user and a playlist
    test_user = User(username="janedoe",
                     email="jane@example.com", password=b"password123")
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    db_session.add(Playlist(title="Jane's Jams",
                   created_by_user_id=test_user.id))
    db_session.commit()

    # 2. Test Success Path
    # Assuming your updated route uses /playlists/me and gets ID from context
    # (If your test client doesn't handle Auth yet, use the /user/<id> route if still present)
    response = client.get(f"/playlists/user/{test_user.id}")
    assert response.status_code == 200
    assert len(response.json()["playlists"]) == 1

    # 3. Test Failure Path (The 'User Not Found' fix)
    # Use an ID that definitely doesn't exist
    response_fail = client.get("/playlists/user/9999")

    assert response_fail.status_code == 404
    assert "not exist" in response_fail.json()["message"].lower()


def test_delete_playlist_unauthorized_integration(client, db_session):
    """
    Tests that User A cannot delete User B's playlist.
    """
    user_a = User(username="user_a", email="a@test.com",
                  password=b"password123")
    user_b = User(username="user_b", email="b@test.com",
                  password=b"password123")
    db_session.add_all([user_a, user_b])
    db_session.commit()
    db_session.refresh(user_a)
    db_session.refresh(user_b)

    # User B owns the playlist
    b_playlist = Playlist(title="B's Secrets", created_by_user_id=user_b.id)
    db_session.add(b_playlist)
    db_session.commit()
    db_session.refresh(b_playlist)

    # User A tries to delete it
    # We pass User A's ID in the request context/payload
    response = client.request(
        "DELETE",
        f"/playlists/{b_playlist.id}",
        json={"created_by_user_id": user_a.id}
    )

    # Assertions: Should be 404/Forbidden, NOT 200 and NOT 500
    assert response.status_code == 404

    # Verify it's STILL in the DB
    still_exists = db_session.get(Playlist, b_playlist.id)
    assert still_exists is not None
