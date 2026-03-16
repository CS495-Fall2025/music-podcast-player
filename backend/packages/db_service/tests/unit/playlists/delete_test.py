from unittest.mock import patch, MagicMock
from rss_music_db_service.playlists import delete
from rss_music_data_model import Playlist


@patch("rss_music_db_service.playlists.delete.make_session")
def test_delete_playlist_success(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    fake_playlist = Playlist(id=1, created_by_user_id=1)
    mock_session.query(Playlist).filter_by().first.return_value = fake_playlist

    result = delete.delete_playlist(playlist_id=1, user_id=1)

    assert result is True
    mock_session.delete.assert_called_once_with(fake_playlist)
    mock_session.commit.assert_called_once()


@patch("rss_music_db_service.playlists.delete.make_session")
def test_delete_playlist_returns_false_if_not_found_or_unauthorized(
    mock_make_session,
) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    mock_session.query(Playlist).filter_by().first.return_value = None

    result = delete.delete_playlist(playlist_id=99, user_id=1)

    assert result is False
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
