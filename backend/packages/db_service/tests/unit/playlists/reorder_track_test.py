from unittest.mock import patch, MagicMock
import pytest

from rss_music_db_service.playlists import reorder_track
from rss_music_data_model import Playlist, PlaylistTrack
from rss_music_db_service.errors import PlaylistNotFoundError


@patch("rss_music_db_service.playlists.reorder_track.make_session")
def test_reorder_track_success(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    fake_playlist = Playlist(id=1, created_by_user_id=1)
    mock_session.query(Playlist).filter_by().first.return_value = fake_playlist

    fake_track = PlaylistTrack(id=3, playlist_id=1, track_url="http://example.com/feed.rss", position=1)
    mock_session.query(PlaylistTrack).filter_by().first.return_value = fake_track
    mock_session.query(PlaylistTrack).filter_by().count.return_value = 3

    result = reorder_track.reorder_track(
        playlist_id=1, user_id=1, track_url="http://example.com/feed.rss", new_position=3
    )

    mock_session.commit.assert_called_once()
    assert result["position"] == 3


@patch("rss_music_db_service.playlists.reorder_track.make_session")
def test_reorder_track_same_position_no_db_write(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    fake_playlist = Playlist(id=1, created_by_user_id=1)
    mock_session.query(Playlist).filter_by().first.return_value = fake_playlist

    fake_track = PlaylistTrack(id=1, playlist_id=1, track_url="http://example.com/feed.rss", position=2)
    mock_session.query(PlaylistTrack).filter_by().first.return_value = fake_track
    mock_session.query(PlaylistTrack).filter_by().count.return_value = 3

    result = reorder_track.reorder_track(
        playlist_id=1, user_id=1, track_url="http://example.com/feed.rss", new_position=2
    )

    mock_session.commit.assert_not_called()
    assert result["position"] == 2


@patch("rss_music_db_service.playlists.reorder_track.make_session")
def test_reorder_track_playlist_not_found_raises(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    mock_session.query(Playlist).filter_by().first.return_value = None

    with pytest.raises(PlaylistNotFoundError):
        reorder_track.reorder_track(
            playlist_id=99, user_id=1, track_url="http://example.com/feed.rss", new_position=1
        )


@patch("rss_music_db_service.playlists.reorder_track.make_session")
def test_reorder_track_track_not_found_raises(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    fake_playlist = Playlist(id=1, created_by_user_id=1)
    mock_session.query(Playlist).filter_by().first.return_value = fake_playlist
    mock_session.query(PlaylistTrack).filter_by().first.return_value = None

    with pytest.raises(PlaylistNotFoundError):
        reorder_track.reorder_track(
            playlist_id=1, user_id=1, track_url="http://example.com/missing.rss", new_position=1
        )
