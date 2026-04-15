from rss_music_data_model import Playlist, PlaylistTrack, User


def test_delete_user_route_not_found(client, db_session) -> None:
    """DELETE /users/{user_id} returns 404 if user doesn't exist."""
    response = client.delete("/users/999")

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "NotFound"


def test_delete_user_route_success(client, db_session) -> None:
    """DELETE /users/{user_id} cascades to playlists and playlist tracks."""
    user = User(
        username="delete_me",
        email="delete_me@domain.com",
        password=b"test-password-hash",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    playlist = Playlist(
        title="Delete Me Playlist",
        created_by_user_id=user.id,
    )
    db_session.add(playlist)
    db_session.commit()
    db_session.refresh(playlist)

    track = PlaylistTrack(
        playlist_id=playlist.id,
        track_url="http://example.com/track.mp3",
        position=1,
    )
    db_session.add(track)
    db_session.commit()

    user_id = user.id
    playlist_id = playlist.id
    track_id = track.id

    response = client.delete(f"/users/{user_id}")

    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    db_session.expire_all()
    assert db_session.get(User, user_id) is None
    assert db_session.get(Playlist, playlist_id) is None
    assert db_session.get(PlaylistTrack, track_id) is None


def test_delete_user_requires_valid_id(client) -> None:
    """DELETE /users/{user_id} with invalid ID format returns error."""
    response = client.delete("/users/invalid")

    # FastAPI path param validation error.
    assert response.status_code == 422
