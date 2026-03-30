from unittest.mock import patch, MagicMock
import pytest

from rss_music_db_service.playlists import get_by_user
from rss_music_db_service.errors import UserNotFoundError
from rss_music_data_model import Playlist, User


@patch("rss_music_db_service.playlists.get_by_user.make_session")
def test_get_playlists_by_user_success(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    mock_session.query(User).filter_by().first.return_value = User(id=1)

    expected_list = [
        Playlist(id=1, title="List 1", created_by_user_id=1),
        Playlist(id=2, title="List 2", created_by_user_id=1),
    ]
    mock_session.query(Playlist).filter_by().all.return_value = expected_list

    result = get_by_user.get_playlists_by_user(user_id=1)

    assert len(result) == 2
    assert result == expected_list
    mock_session.query.assert_any_call(User)
    mock_session.query.assert_any_call(Playlist)


@patch("rss_music_db_service.playlists.get_by_user.make_session")
def test_get_playlists_by_user_raises_not_found(mock_make_session) -> None:
    """Tests that a non-existent user ID raises UserNotFoundError instead of returning []"""
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    with pytest.raises(UserNotFoundError) as excinfo:
        get_by_user.get_playlists_by_user(user_id=999)

    assert "User with ID 999 does not exist" in str(excinfo.value)

    mock_session.query.assert_called_with(User)

    for call in mock_session.query.call_args_list:
        assert call.args[0] != Playlist
