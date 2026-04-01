from datetime import datetime
from unittest.mock import patch, MagicMock
import pytest

from rss_music_db_service.playlists import get_by_id
from rss_music_data_model import Playlist, PlaylistTrack
from rss_music_db_service.errors import PlaylistNotFoundError


@patch("rss_music_db_service.playlists.get_by_id.make_session")
def test_get_playlist_by_id_success(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    added_at = datetime(2026, 1, 1)
    fake_track = PlaylistTrack(
        id=1, playlist_id=5, track_url="http://example.com/feed.rss", position=1
    )
    fake_track.added_at = added_at

    fake_playlist = Playlist(
        id=5,
        title="My Playlist",
        description="desc",
        track_count=1,
        created_by_user_id=99,
    )
    fake_playlist.created_at = datetime(2026, 1, 1)
    fake_playlist.tracks = [fake_track]

    mock_session.query(Playlist).filter_by().first.return_value = fake_playlist

    result = get_by_id.get_playlist_by_id(playlist_id=5)

    assert result["id"] == 5
    assert result["title"] == "My Playlist"
    assert len(result["tracks"]) == 1
    assert result["tracks"][0]["track_url"] == "http://example.com/feed.rss"
    assert result["tracks"][0]["position"] == 1


@patch("rss_music_db_service.playlists.get_by_id.make_session")
def test_get_playlist_by_id_not_found_raises(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    mock_session.query(Playlist).filter_by().first.return_value = None

    with pytest.raises(PlaylistNotFoundError):
        get_by_id.get_playlist_by_id(playlist_id=999)
