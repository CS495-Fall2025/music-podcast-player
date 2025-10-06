import hashlib
import os
import time

from rss_music_backend.external_apis.abc import SearchFeedsClient, SearchFeedsParser
from rss_music_backend.external_apis.auth import identity


class PodcastIndexAPI(SearchFeedsClient, SearchFeedsParser):
    # Follows https://podcastindex-org.github.io/docs-api/#auth
    @classmethod
    def _create_current_auth_headers(cls) -> dict[str, str]:
        user_agent = identity.get_user_agent()
        key = os.getenv("PODCAST_INDEX_KEY")
        secret = os.getenv("PODCAST_INDEX_SECRET")
        date = int(time.now())

        return cls._create_auth_headers(user_agent, key, secret, date)

    @classmethod
    def _create_auth_headers(
            cls, user_agent: str, key: str, secret: str, date: int
    ) -> dict[str, str]:
        auth_hash = hashlib.sha1(f"{key}{secret}{date}".encode("UTF-8")).hexdigest()

        return {
            "User-Agent": user_agent,
            "X-Auth-Key": key,
            "X-Auth-Date": str(date),
            "Authorization": auth_hash,
        }

