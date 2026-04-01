from unittest.mock import patch, MagicMock
import pytest

from rss_music_db_service.playlists import remove_track
from rss_music_data_model import Playlist, PlaylistTrack
from rss_music_db_service.errors import PlaylistNotFoundError


@patch("rss_music_db_service.playlists.remove_track.make_session")
def test_remove_track_success(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    fake_playlist = Playlist(id=1, created_by_user_id=1, track_count=2)
    fake_track = PlaylistTrack(id=7, playlist_id=1, track_url="http://example.com/feed.rss", position=1)
    mock_session.query.return_value.filter_by.return_value.first.side_effect = [fake_playlist, fake_track]

    result = remove_track.remove_track_from_playlist(
        playlist_id=1, user_id=1, track_url="http://example.com/feed.rss"
    )

    mock_session.delete.assert_called_once_with(fake_track)
    mock_session.commit.assert_called_once()
    assert result == 7
    assert fake_playlist.track_count == 1


@patch("rss_music_db_service.playlists.remove_track.make_session")
def test_remove_track_playlist_not_found_raises(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    mock_session.query(Playlist).filter_by().first.return_value = None

    with pytest.raises(PlaylistNotFoundError):
        remove_track.remove_track_from_playlist(
            playlist_id=99, user_id=1, track_url="http://example.com/feed.rss"
        )

    mock_session.delete.assert_not_called()


@patch("rss_music_db_service.playlists.remove_track.make_session")
def test_remove_track_track_not_found_raises(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    fake_playlist = Playlist(id=1, created_by_user_id=1, track_count=1)
    mock_session.query.return_value.filter_by.return_value.first.side_effect = [fake_playlist, None]

    with pytest.raises(PlaylistNotFoundError):
        remove_track.remove_track_from_playlist(
            playlist_id=1, user_id=1, track_url="http://example.com/missing.rss"
        )

    mock_session.delete.assert_not_called()
