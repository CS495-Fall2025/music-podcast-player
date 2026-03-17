from rss_music_data_model import User, Playlist


def test_create_playlist_integration(client, db_session):
    """
    Tests the full flow: API -> DB -> Response
    Covers the 'missing description' and 'int vs string' bugs.
    """
    test_user = User(
        username="johndoe", email="john@example.com", password=b"password123"
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    payload = {
        "title": "My First Playlist",
        "created_by_user_id": test_user.id,
    }

    response = client.post("/playlists/create", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My First Playlist"
    assert data["created_by_user_id"] == test_user.id

    db_playlist = (
        db_session.query(Playlist).filter_by(title="My First Playlist").first()
    )
    assert db_playlist is not None
    assert db_playlist.created_by_user_id == test_user.id


def test_create_playlist_user_not_found(client, db_session):
    """Tests that creating a playlist for a non-existing user returns a 404"""

    payload = {
        "title": "NULL's Playlist",
        "created_by_user_id": 9999,
    }

    response = client.post("/playlists/create", json=payload)

    assert response.status_code == 404
    assert response.json()["error"] == "NotFound"


def test_get_playlists_me_success(client, db_session):
    """Tests that a valid user can retrieve their playlists"""
    test_user = User(
        username="janedoe", email="jane@example.com", password=b"password123"
    )

    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    db_session.add(Playlist(title="Jane's Playlist", created_by_user_id=test_user.id))
    db_session.commit()

    response = client.get(f"/playlists/user/{test_user.id}")

    assert response.status_code == 200
    assert len(response.json()["playlists"]) == 1
    assert response.json()["playlists"][0]["title"] == "Jane's Playlist"


def test_get_playlists_me_user_not_found(client, db_session):
    """Tests that requesting playlists for a non-existing user returns 404"""

    response = client.get("/playlists/user/9999")

    assert response.status_code == 404
    assert response.json()["error"] == "NotFound"
    assert "not exist" in response.json()["message"].lower()


def test_delete_playlist_unauthorized_integration(client, db_session):
    """
    Tests that User A cannot delete User B's playlist.
    """
    user_a = User(username="user_a", email="a@test.com", password=b"password123")
    user_b = User(username="user_b", email="b@test.com", password=b"password123")
    db_session.add_all([user_a, user_b])
    db_session.commit()
    db_session.refresh(user_a)
    db_session.refresh(user_b)

    b_playlist = Playlist(title="B's Secrets", created_by_user_id=user_b.id)
    db_session.add(b_playlist)
    db_session.commit()
    db_session.refresh(b_playlist)

    response = client.request(
        "DELETE", f"/playlists/{b_playlist.id}", json={"created_by_user_id": user_a.id}
    )

    assert response.status_code == 404
    assert response.json()["error"] == "NotFound"
    assert "unauthorized" in response.json()["message"].lower()

    still_exists = db_session.get(Playlist, b_playlist.id)

    assert still_exists is not None


def test_update_playlist_not_found(client, db_session):
    """Tests that updating a non-existing playlist returns the proper error"""

    payload = {
        "title": "New Playlist",
        "created_by_user_id": 1,
    }

    response = client.put("playlists/9999", json=payload)

    assert response.status_code == 404
    assert response.json()["error"] == "NotFound"
    assert "not found" in response.json()["message"].lower()
