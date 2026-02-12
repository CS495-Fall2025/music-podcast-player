from importlib.metadata import version

PACKAGE_NAME = "rss_music_api_service"
USER_AGENT_NAME = "RSSMusicPlayer"


def get_user_agent() -> str:
    return f"{USER_AGENT_NAME}/{version(PACKAGE_NAME)}"
