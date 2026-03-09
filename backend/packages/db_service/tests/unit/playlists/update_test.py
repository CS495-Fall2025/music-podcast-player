from unittest.mock import patch, MagicMock

from rss_music_db_service.playlists import update
from rss_music_data_model import Playlist


@patch("rss_music_db_service.playlists.update.make_session")
def test_update_playlist_success(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    existing_playlist = Playlist(
        id=5, title="Old Title", description="Old Desc", created_by_user_id=1
    )

    mock_query = mock_session.query.return_value
    mock_filter = mock_query.filter_by.return_value
    mock_filter.first.return_value = existing_playlist

    result = update.update_playlist(
        playlist_id=5, user_id=1, title="New Title", description="New Desc"
    )

    assert result is not None
    assert result.title == "New Title"
    assert result.description == "New Desc"

    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing_playlist)


@patch("rss_music_db_service.playlists.update.make_session")
def test_update_playlist_returns_none_if_not_found(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    result = update.update_playlist(playlist_id=99, user_id=1, title="New")

    assert result is None
    mock_session.commit.assert_not_called()
