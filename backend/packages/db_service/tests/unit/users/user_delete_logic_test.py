from unittest.mock import MagicMock, patch

from rss_music_db_service.users import delete


@patch("rss_music_db_service.users.delete.make_session")
@patch("rss_music_db_service.users.delete.log_request")
def test_delete_user_success(mock_log, mock_make_session) -> None:
    """delete_user returns True and lets the database cascade related rows."""
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    mock_user = MagicMock(id=1)

    mock_session.query.return_value.filter_by.return_value.first.return_value = (
        mock_user
    )

    result = delete.delete_user(user_id=1)

    assert result is True
    mock_session.delete.assert_called_once_with(mock_user)
    mock_session.commit.assert_called_once()
    mock_log.assert_called_once()


@patch("rss_music_db_service.users.delete.make_session")
@patch("rss_music_db_service.users.delete.log_request")
def test_delete_user_not_found(mock_log, mock_make_session) -> None:
    """delete_user returns False if user doesn't exist."""
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    result = delete.delete_user(user_id=999)

    assert result is False
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_log.assert_not_called()


@patch("rss_music_db_service.users.delete.make_session")
@patch("rss_music_db_service.users.delete.log_request")
def test_delete_user_with_no_playlists(mock_log, mock_make_session) -> None:
    """delete_user deletes user without loading related playlists."""
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    mock_user = MagicMock(id=1)

    mock_session.query.return_value.filter_by.return_value.first.return_value = (
        mock_user
    )
    mock_session.query.return_value.filter_by.return_value.all.return_value = []

    result = delete.delete_user(user_id=1)

    assert result is True
    mock_session.delete.assert_called_once_with(mock_user)
    mock_session.commit.assert_called_once()
    mock_log.assert_called_once()
