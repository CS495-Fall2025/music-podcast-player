from unittest.mock import patch, MagicMock

from rss_music_db_service.playlists import get_by_user
from rss_music_data_model import Playlist


@patch("rss_music_db_service.playlists.get_by_user.make_session")
def test_get_playlists_by_user(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    expected_list = [
        Playlist(id=1, title="List 1", created_by_user_id=1),
        Playlist(id=2, title="List 2", created_by_user_id=1),
    ]

    # Mock session.query().filter_by().all()
    mock_session.query.return_value.filter_by.return_value.all.return_value = (
        expected_list
    )

    result = get_by_user.get_playlists_by_user(user_id=1)

    assert len(result) == 2
    assert result == expected_list
    mock_session.query.assert_called_once_with(Playlist)
