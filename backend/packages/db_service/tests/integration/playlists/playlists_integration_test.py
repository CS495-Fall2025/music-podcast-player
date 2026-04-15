from rss_music_data_model import User, Playlist, PlaylistTrack


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


# --- Track operation tests ---


def _make_user_and_playlist(db_session):
    user = User(username="trackuser", email="track@example.com", password=b"pw")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    playlist = Playlist(title="Track Test Playlist", created_by_user_id=user.id)
    db_session.add(playlist)
    db_session.commit()
    db_session.refresh(playlist)

    return user, playlist


def test_add_track_success(client, db_session):
    user, playlist = _make_user_and_playlist(db_session)

    response = client.post(
        f"/playlists/{playlist.id}/tracks/add",
        json={
            "track_url": "http://example.com/feed.rss",
            "created_by_user_id": user.id,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["track_url"] == "http://example.com/feed.rss"
    assert data["position"] == 1

    track = db_session.query(PlaylistTrack).filter_by(playlist_id=playlist.id).first()
    assert track is not None

    db_session.refresh(playlist)
    assert playlist.track_count == 1


def test_add_track_playlist_not_found(client, db_session):
    response = client.post(
        "/playlists/9999/tracks/add",
        json={"track_url": "http://example.com/feed.rss", "created_by_user_id": 1},
    )

    assert response.status_code == 404
    assert response.json()["error"] == "NotFound"


def test_add_track_unauthorized(client, db_session):
    """User B cannot add tracks to User A's playlist."""
    user, playlist = _make_user_and_playlist(db_session)

    response = client.post(
        f"/playlists/{playlist.id}/tracks/add",
        json={
            "track_url": "http://example.com/feed.rss",
            "created_by_user_id": user.id + 999,
        },
    )

    assert response.status_code == 404


def test_add_track_duplicate_returns_conflict(client, db_session):
    user, playlist = _make_user_and_playlist(db_session)

    payload = {
        "track_url": "http://example.com/feed.rss",
        "created_by_user_id": user.id,
    }
    client.post(f"/playlists/{playlist.id}/tracks/add", json=payload)
    response = client.post(f"/playlists/{playlist.id}/tracks/add", json=payload)

    assert response.status_code == 409


def test_remove_track_success(client, db_session):
    user, playlist = _make_user_and_playlist(db_session)

    client.post(
        f"/playlists/{playlist.id}/tracks/add",
        json={
            "track_url": "http://example.com/feed.rss",
            "created_by_user_id": user.id,
        },
    )

    response = client.request(
        "DELETE",
        f"/playlists/{playlist.id}/tracks/remove",
        json={
            "track_url": "http://example.com/feed.rss",
            "created_by_user_id": user.id,
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Track removed"

    track = db_session.query(PlaylistTrack).filter_by(playlist_id=playlist.id).first()
    assert track is None


def test_remove_track_not_found(client, db_session):
    user, playlist = _make_user_and_playlist(db_session)

    response = client.request(
        "DELETE",
        f"/playlists/{playlist.id}/tracks/remove",
        json={
            "track_url": "http://example.com/missing.rss",
            "created_by_user_id": user.id,
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "NotFound"


def test_get_playlist_by_id_success(client, db_session):
    user, playlist = _make_user_and_playlist(db_session)

    client.post(
        f"/playlists/{playlist.id}/tracks/add",
        json={
            "track_url": "http://example.com/feed.rss",
            "created_by_user_id": user.id,
        },
    )

    response = client.get(f"/playlists/{playlist.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == playlist.id
    assert data["title"] == "Track Test Playlist"
    assert len(data["tracks"]) == 1
    assert data["tracks"][0]["track_url"] == "http://example.com/feed.rss"
    assert data["tracks"][0]["position"] == 1


def test_get_playlist_by_id_not_found(client, db_session):
    response = client.get("/playlists/9999")

    assert response.status_code == 404
    assert response.json()["error"] == "NotFound"


def test_reorder_track_success(client, db_session):
    user, playlist = _make_user_and_playlist(db_session)

    for url in [
        "http://example.com/a.rss",
        "http://example.com/b.rss",
        "http://example.com/c.rss",
    ]:
        client.post(
            f"/playlists/{playlist.id}/tracks/add",
            json={"track_url": url, "created_by_user_id": user.id},
        )

    # Move track at position 1 to position 3
    response = client.patch(
        f"/playlists/{playlist.id}/tracks/reorder",
        json={
            "track_url": "http://example.com/a.rss",
            "new_position": 3,
            "created_by_user_id": user.id,
        },
    )

    assert response.status_code == 200
    assert response.json()["position"] == 3

    # Confirm the other tracks shifted up
    b = (
        db_session.query(PlaylistTrack)
        .filter_by(playlist_id=playlist.id, track_url="http://example.com/b.rss")
        .first()
    )
    c = (
        db_session.query(PlaylistTrack)
        .filter_by(playlist_id=playlist.id, track_url="http://example.com/c.rss")
        .first()
    )
    assert b.position == 1
    assert c.position == 2


def test_reorder_track_not_found(client, db_session):
    user, playlist = _make_user_and_playlist(db_session)

    response = client.patch(
        f"/playlists/{playlist.id}/tracks/reorder",
        json={
            "track_url": "http://example.com/missing.rss",
            "new_position": 1,
            "created_by_user_id": user.id,
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "NotFound"
