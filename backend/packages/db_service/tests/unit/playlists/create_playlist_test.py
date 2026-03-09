from unittest.mock import patch, MagicMock
import pytest
from sqlalchemy.exc import IntegrityError

from rss_music_db_service.playlists import create
from rss_music_data_model import Playlist


@patch("rss_music_db_service.playlists.create.make_session")
def test_create_and_add_playlist_success(mock_make_session) -> None:
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


@patch("rss_music_db_service.playlists.create.make_session")
def test_create_and_add_playlist_rolls_back_on_integrity_error(
    mock_make_session,
) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    mock_session.commit.side_effect = IntegrityError(
        "mock error", params=None, orig=None
    )

    with pytest.raises(IntegrityError):
        create.create_and_add_playlist(title="Title", user_id=1)

    mock_session.rollback.assert_called_once()
