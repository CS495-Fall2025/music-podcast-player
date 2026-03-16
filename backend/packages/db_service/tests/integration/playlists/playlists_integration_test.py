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


def test_get_playlists_me_integration(client, db_session):
    """
    Tests the 'Get Playlists' flow and ensures we handle non-existent users with 404.
    """
    test_user = User(
        username="janedoe", email="jane@example.com", password=b"password123"
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    db_session.add(Playlist(title="Jane's Jams", created_by_user_id=test_user.id))
    db_session.commit()

    response = client.get(f"/playlists/user/{test_user.id}")
    assert response.status_code == 200
    assert len(response.json()["playlists"]) == 1

    response_fail = client.get("/playlists/user/9999")

    assert response_fail.status_code == 404
    assert "not exist" in response_fail.json()["message"].lower()


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

    still_exists = db_session.get(Playlist, b_playlist.id)
    assert still_exists is not None
