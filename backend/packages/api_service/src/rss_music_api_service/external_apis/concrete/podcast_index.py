import hashlib
import time
from urllib.parse import urljoin

from flask import current_app
from marshmallow import ValidationError
import requests

from rss_music_api_service.data import Feed
from rss_music_api_service.external_apis.auth import identity
from rss_music_api_service.external_apis import errors
from rss_music_api_service.schemas import SearchFeedsResponseSchema
from rss_music_api_service.logging_config import log_request, get_logger

API_URL = "https://api.podcastindex.org/api/1.0/"
TIMEOUT = (3, 10)  # 3 Seconds to connect, 10 seconds to recieve response.
logger = get_logger(__name__)


# Using https://podcastindex-org.github.io/docs-api/#get-/search/music/byterm
class PodcastIndexAPI:
    @classmethod
    def search_music_feeds(
        cls, query: str, count: int = 25, start: int = 0
    ) -> list[Feed]:
        with requests.Session() as session:
            auth_headers = cls._create_current_auth_headers()
            request, context = cls._make_search_request(
                query, count, start, auth_headers
            )

            log_request(
                logger,
                "info",
                "external_request_sent",
                "Request sent to PodcastIndex API",
                service="PodcastIndexAPI",
                url=request.url,
            )

            try:
                response = session.send(request, timeout=TIMEOUT)

                level = "info" if response.status_code < 400 else "warn"
                log_request(
                    logger,
                    level,
                    "external_response_received",
                    "Response received from PodcastIndex API",
                    service="PodcastIndexAPI",
                    status_code=response.status_code,
                )
            except requests.Timeout:
                log_request(
                    logger,
                    "error",
                    "external_timeout",
                    "PodcastIndex API timeout",
                    service="PodcastIndexAPI",
                )
                raise errors.ExternalAPITimeoutError("PodcastIndexAPI")
            except requests.RequestException as e:
                log_request(
                    logger,
                    "error",
                    "external_error",
                    "Error sending request to PodcastIndex API",
                    service="PodcastIndexAPI",
                    error=str(e),
                )
                raise errors.ExternalAPITransportError(
                    "An error occurred while sending a request to the PodcastIndexAPI"
                )

        return cls._parse_search_response(response, context)[start : (start + count)]

    @classmethod
    def _make_search_request(
        cls, query: str, count: int, start: int, auth_headers: dict[str, str]
    ) -> tuple[requests.PreparedRequest, dict]:
        url = urljoin(API_URL, "search/music/byterm")
        data = {
            "q": query,
            "max": start + count,
        }
        request = requests.Request("GET", url, auth_headers, params=data)

        return (request.prepare(), {"count": count, "start": start})

    @classmethod
    def _parse_search_response(
        cls, response: requests.Response, context: dict
    ) -> list[Feed]:
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
                case 429:
                    raise errors.ExternalAPITooManyRequestsError(
                        "Recieved 429 too many requests from the PodcastIndex API"
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
        except ValidationError as error:
            raise errors.ExternalAPIInvalidResponseDataError(
                f"PodcastIndex API response did not match expected schema: {error.messages}"
            )

        feeds = []
        for feed_data in validated_response["feeds"]:
            # It may be better to use a schema for this in the future, but this
            # should be good for now.
            feeds.append(
                Feed(
                    url=feed_data["url"],
                    # It is possible for the PodcastIndex to return image but not
                    # artwork. In the event it returns neither the frontend will display
                    # a default image.
                    art_url=feed_data["artwork"] if feed_data["artwork"] else feed_data["image"],
                    title=feed_data["title"],
                    artist=feed_data["author"],
                )
            )

        return feeds

    # Follows https://podcastindex-org.github.io/docs-api/#auth
    @classmethod
    def _create_current_auth_headers(cls) -> dict[str, str]:
        user_agent = identity.get_user_agent()
        key = current_app.config["PODCAST_INDEX_KEY"]
        secret = current_app.config["PODCAST_INDEX_SECRET"]
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
