from unittest.mock import patch, MagicMock
import pytest
from sqlalchemy.exc import IntegrityError

from rss_music_db_service.playlists import add_track
from rss_music_data_model import Playlist, PlaylistTrack
from rss_music_db_service.errors import PlaylistNotFoundError, TrackAlreadyExistsError


@patch("rss_music_db_service.playlists.add_track.make_session")
def test_add_track_success(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    fake_playlist = Playlist(id=1, created_by_user_id=42, track_count=0)
    mock_session.query(Playlist).filter_by().first.return_value = fake_playlist
    mock_session.query(PlaylistTrack).filter_by().count.return_value = 2

    result = add_track.add_track_to_playlist(
        playlist_id=1, user_id=42, track_url="http://example.com/feed.rss"
    )

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    assert result["track_url"] == "http://example.com/feed.rss"
    assert result["position"] == 3


@patch("rss_music_db_service.playlists.add_track.make_session")
def test_add_track_playlist_not_found_raises(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    mock_session.query(Playlist).filter_by().first.return_value = None

    with pytest.raises(PlaylistNotFoundError):
        add_track.add_track_to_playlist(
            playlist_id=99, user_id=1, track_url="http://example.com/feed.rss"
        )

    mock_session.add.assert_not_called()


@patch("rss_music_db_service.playlists.add_track.make_session")
def test_add_track_duplicate_raises(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    fake_playlist = Playlist(id=1, created_by_user_id=1, track_count=1)
    mock_session.query(Playlist).filter_by().first.return_value = fake_playlist
    mock_session.query(PlaylistTrack).filter_by().count.return_value = 1
    mock_session.commit.side_effect = IntegrityError(
        "UNIQUE constraint failed", params=None, orig=None
    )

    with pytest.raises(TrackAlreadyExistsError):
        add_track.add_track_to_playlist(
            playlist_id=1, user_id=1, track_url="http://example.com/feed.rss"
        )

    mock_session.rollback.assert_called_once()
