from unittest.mock import patch, MagicMock
import pytest
from sqlalchemy.exc import IntegrityError

from rss_music_db_service.playlists import create
from rss_music_data_model import Playlist
from rss_music_db_service.errors import UserNotFoundError


@patch("rss_music_db_service.playlists.create.log_request")
@patch("rss_music_db_service.playlists.create.make_session")
def test_create_and_add_playlist_success(mock_make_session, mock_log) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    expected_title = "My Summer Mix"
    expected_user_id = 1
    expected_desc = "Vibes"

    playlist = create.create_and_add_playlist(
        title=expected_title, user_id=expected_user_id, description=expected_desc
    )

    assert isinstance(playlist, Playlist)
    assert playlist.title == expected_title
    assert playlist.created_by_user_id == expected_user_id
    assert playlist.description == expected_desc

    mock_session.add.assert_called_once_with(playlist)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(playlist)

    mock_log.assert_called_once()
    assert mock_log.call_args[0][3] == "Playlist created"


@patch("rss_music_db_service.playlists.create.make_session")
def test_create_and_add_playlist_raises_user_not_found(mock_make_session) -> None:
    """Tests that an IntegrityError (FK violation) is transformed into UserNotFoundError"""
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    mock_session.commit.side_effect = IntegrityError(
        "foreign key constraint failed", params=None, orig=None
    )

    with pytest.raises(UserNotFoundError) as excinfo:
        create.create_and_add_playlist(title="Title", user_id=999)

    assert "User ID 999 does not exist" in str(excinfo.value)
    mock_session.rollback.assert_called_once()


@patch("rss_music_db_service.playlists.create.make_session")
def test_create_and_add_playlist_no_description(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    playlist = create.create_and_add_playlist(title="Minimalist", user_id=1)

    assert playlist.description is None
    mock_session.add.assert_called_once()
