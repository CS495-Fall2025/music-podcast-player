import hashlib
import os
import time
from urllib.parse import urljoin

from requests import Request, PreparedRequest, Response

from rss_music_backend.data import Feed
from rss_music_backend.external_apis.auth import identity
from rss_music_backend.external_apis.errors import ExternalError

API_URL = "https://api.podcastindex.org/api/1.0/"


class PodcastIndexAPI:
    # Using https://podcastindex-org.github.io/docs-api/#get-/search/music/byterm
    @classmethod
    def search_music_feeds(
                cls, query: str, count: int, start: int
    ) -> list[Feed] | ExternalError:
        pass

    @classmethod
    def _make_search_request(
            cls, query: str, count: int, start: int
    ) -> tuple[PreparedRequest, dict]:
        url = urljoin(API_URL, "search/music/byterm")
        data = {
            "q": query,
            "max": start + count,
        }
        headers = cls._create_current_auth_headers()

        request = Request("GET", url, headers, json=data)

        return (request.prepare(), {"count": count, "start": start})

    @classmethod
    def _parse_search_response(
            cls, response: Response, context: dict
    ) -> list[Feed] | ExternalError:
        pass

    # Follows https://podcastindex-org.github.io/docs-api/#auth
    @classmethod
    def _create_current_auth_headers(cls) -> dict[str, str]:
        user_agent = identity.get_user_agent()
        key = os.getenv("PODCAST_INDEX_KEY")
        secret = os.getenv("PODCAST_INDEX_SECRET")
        date = int(time.time())

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

