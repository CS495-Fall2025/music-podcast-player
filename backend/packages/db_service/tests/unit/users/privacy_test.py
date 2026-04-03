from unittest.mock import patch, MagicMock

from rss_music_db_service.users import privacy
from rss_music_data_model import User


@patch("rss_music_db_service.users.privacy.make_session")
def test_get_profile_public_returns_true_when_public(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    fake_user = User(id=1)
    fake_user.profile_public = True
    mock_session.query.return_value.filter_by.return_value.first.return_value = (
        fake_user
    )

    result = privacy.get_profile_public(1)

    assert result is True


@patch("rss_music_db_service.users.privacy.make_session")
def test_get_profile_public_returns_false_when_private(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    fake_user = User(id=1)
    fake_user.profile_public = False
    mock_session.query.return_value.filter_by.return_value.first.return_value = (
        fake_user
    )

    result = privacy.get_profile_public(1)

    assert result is False


@patch("rss_music_db_service.users.privacy.make_session")
def test_get_profile_public_defaults_true_when_user_not_found(
    mock_make_session,
) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    result = privacy.get_profile_public(999)

    assert result is True


@patch("rss_music_db_service.users.privacy.make_session")
def test_set_profile_public_updates_and_commits(mock_make_session) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    fake_user = User(id=1)
    fake_user.profile_public = True
    mock_session.query.return_value.filter_by.return_value.first.return_value = (
        fake_user
    )

    result = privacy.set_profile_public(1, False)

    assert result is True
    assert fake_user.profile_public is False
    mock_session.commit.assert_called_once()


@patch("rss_music_db_service.users.privacy.make_session")
def test_set_profile_public_returns_false_when_user_not_found(
    mock_make_session,
) -> None:
    mock_session = MagicMock()
    mock_make_session.return_value.__enter__.return_value = mock_session

    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    result = privacy.set_profile_public(999, True)

    assert result is False
    mock_session.commit.assert_not_called()
