import hashlib
import os
import time
from urllib.parse import urljoin

import requests

from rss_music_backend.data import Feed
from rss_music_backend.external_apis.auth import identity
from rss_music_backend.external_apis import errors
from rss_music_backend.schemas import SearchFeedsResponseSchema

API_URL = "https://api.podcastindex.org/api/1.0/"
TIMEOUT = (3, 10) # 3 Seconds to connect, 10 seconds to recieve response.


class PodcastIndexAPI:
    # Using https://podcastindex-org.github.io/docs-api/#get-/search/music/byterm
    @classmethod
    def search_music_feeds(cls, query: str, count: int, start: int) -> list[Feed]:
        with requests.Session() as session:
            request, context = cls._make_search_request(query, count, start)

            try:
                response = session.send(request, timeout=TIMEOUT)
            except requests.Timeout:
                raise errors.TimeoutError("PodcastIndexAPI")
            except requests.RequestException:
                raise errors.ExternalAPITransportError(
                    "An error occurred while sending a request to the PodcastIndexAPI"
                )

        return cls._parse_search_response(response, context)


    @classmethod
    def _make_search_request(
            cls, query: str, count: int, start: int
    ) -> tuple[requests.PreparedRequest, dict]:
        url = urljoin(API_URL, "search/music/byterm")
        data = {
            "q": query,
            "max": start + count,
        }
        headers = cls._create_current_auth_headers()

        request = requests.Request("GET", url, headers, json=data)

        return (request.prepare(), {"count": count, "start": start})

    @classmethod
    def _parse_search_response(cls, response: requests.Response, context: dict) -> list[Feed]:
        if not response.status_code == 200:
            # Status codes possible as described by https://podcastindex-org.github.io/docs-api/
            match response.status_code:
                case 400:
                    raise errors.ExternalAPIBadRequestError(
                        "Recieved 400 bad request from the PodcastIndex API"
                    )
                case 401:
                    raise errors.ExternalAPIBadAuthenticationError(
                        "Recieved 401 bad authentication from the PodcastIndex API"
                    )
                case _:
                    raise errors.ExternalAPIReturnedError(
                        f"Recieved code {response.status_code} from the PodcastIndex API"
                    )

        try:
            data = response.json()
            validated_response = SearchFeedsResponseSchema().load(data)

        except requests.JSONDecodeError:
            raise errors.ExternalAPIInvalidResponseFormatError(
                "Could not parse non-json response from the PodcastIndex API"
            )
        except ValidationError:
            raise errors.ExternalAPIInvalidResponseDataError(
                "PodcastIndex API response did not match expected schema"
            )

        # Continue processing the response here, convert it into a bunch of Feeds and 
        # return them.

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

