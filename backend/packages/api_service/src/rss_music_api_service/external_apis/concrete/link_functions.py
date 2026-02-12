import requests

from rss_music_api_service.data import Rss
from rss_music_api_service.external_apis.auth import identity
from rss_music_api_service.external_apis import errors
from rss_music_api_service.logging_config import log_request, get_logger

import xml.etree.ElementTree as ET

TIMEOUT = (3, 10)

MAX_FEED_SIZE = 10_000_000
logger = get_logger(__name__)


class LinkFunctions:
    @classmethod
    def make_link_feed_request(cls, url: str) -> dict:
        request = requests.Request("GET", url)
        return request.prepare()

    @classmethod
    def parse_link_feed_response(cls, response: requests.Response) -> Rss:
        if len(response.content) > MAX_FEED_SIZE:
            raise errors.ExternalAPIBadRequestError(
                "The RSS Feed was too large in size to parse"
            )

        if not response.status_code == 200:
            match response.status_code:
                case 400:
                    raise errors.ExternalAPIBadRequestError(
                        "Recieved 400: Bad Request from the Link Endpoint"
                    )
                case 401:
                    raise errors.ExternalAPIBadAuthenticationError(
                        "Recieved 401: Bad Authentication from the Link Endpoint"
                    )
                case 405:
                    raise errors.ExternalAPIBadRequestError(
                        "Recieved 405: Method Not Allowed"
                    )
                case _:
                    raise errors.ExternalAPIReturnedError(
                        f"Recieved code {response.status_code} from the Link Endpoint"
                    )

        ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
        PODCAST_NS = "https://podcastindex.org/namespace/1.0"

        def it(tag: str) -> str:
            return f"{{{ITUNES_NS}}}{tag}"

        def pc(tag: str) -> str:
            return f"{{{PODCAST_NS}}}{tag}"

        try:
            root = ET.fromstring(response.content)
            if root is None:
                raise errors.ExternalAPIInvalidResponseDataError("Invalid XML")
            podcast_check = any(
                child.tag.startswith(f"{{{PODCAST_NS}}}") for child in root.iter()
            )
            if not podcast_check:
                raise errors.ExternalAPIBadRequestError(
                    "Requested link is not of podcast type"
                )
            channel = root.find("channel")
            if channel is None:
                raise errors.ExternalAPIInvalidResponseDataError(
                    "RSS Feed response did not contain data"
                )

            if channel.findtext(it("title")):
                title = channel.findtext(it("title")).strip()
            elif channel.findtext("title"):
                title = channel.findtext("title").strip()
            elif channel.findtext("itunes:title"):
                title = channel.findtext("itunes:title").strip()
            elif channel.findtext(pc("title")):
                title = channel.findtext(pc("title")).strip()
            else:
                title = "Unknown"

            if channel.findtext(it("description")):
                description = channel.findtext(it("description")).strip()
            elif channel.findtext("description"):
                description = channel.findtext("description").strip()
            elif channel.findtext("itunes:description"):
                description = channel.findtext("itunes:description").strip()
            elif channel.findtext(pc("description")):
                description = channel.findtext(pc("description")).strip()
            else:
                description = "Unknown"

            if channel.findtext(it("author")):
                author = channel.findtext(it("author")).strip()
            elif channel.findtext("author"):
                author = channel.findtext("author").strip()
            elif channel.findtext("itunes:author"):
                author = channel.findtext("itunes:author").strip()
            elif channel.findtext(pc("author")):
                author = channel.findtext(pc("author")).strip()
            else:
                author = "Unknown"

            if channel.findtext(it("link")):
                link = channel.findtext(it("link")).strip()
            elif channel.findtext("link"):
                link = channel.findtext("link").strip()
            elif channel.findtext("itunes:link"):
                link = channel.findtext("itunes:link").strip()
            elif channel.findtext(pc("link")):
                link = channel.findtext(pc("link")).strip()
            else:
                link = response.url

            if channel.findtext(it("language")):
                language = channel.findtext(it("language")).strip()
            elif channel.findtext("language"):
                language = channel.findtext("language").strip()
            elif channel.findtext("itunes:language"):
                language = channel.findtext("itunes:language").strip()
            elif channel.findtext(pc("language")):
                language = channel.findtext(pc("language")).strip()
            else:
                language = "Unknown"

            if channel.findtext(it("pubDate")):
                pubDate = channel.findtext(it("pubDate")).strip()
            elif channel.findtext("pubDate"):
                pubDate = channel.findtext("pubDate").strip()
            elif channel.findtext("itunes:pubDate"):
                pubDate = channel.findtext("itunes:pubDate").strip()
            elif channel.findtext(pc("pubDate")):
                pubDate = channel.findtext(pc("pubDate")).strip()
            else:
                pubDate = "Unknown"

            if channel.findtext(it("lastBuildDate")):
                lastBuildDate = channel.findtext(it("lastBuildDate")).strip()
            elif channel.findtext("lastBuildDate"):
                lastBuildDate = channel.findtext("lastBuildDate").strip()
            elif channel.findtext("itunes:lastBuildDate"):
                lastBuildDate = channel.findtext("itunes:lastBuildDate").strip()
            elif channel.findtext(pc("lastBuildDate")):
                lastBuildDate = channel.findtext(pc("lastBuildDate")).strip()
            else:
                lastBuildDate = "Unknown"

            value_element = channel.find(pc("value"))

            valueType = ""
            valueMethod = ""
            value_items = []

            if value_element is not None:
                valueType = value_element.get("type", "").strip()
                valueMethod = value_element.get("method", "").strip()
                val_recipient_tag = value_element.findall(pc("valueRecipient"))
                if val_recipient_tag is not None:
                    for val_recipient in val_recipient_tag:
                        value_items.append(
                            {
                                "type": valueType,
                                "method": valueMethod,
                                "Name": val_recipient.get("name", "").strip(),
                                "Type": val_recipient.get("type", "").strip(),
                                "Address": val_recipient.get("address", "").strip(),
                                "CustomKey": val_recipient.get("customKey", "").strip(),
                                "CustomValue": val_recipient.get(
                                    "customValue", ""
                                ).strip(),
                                "Split": val_recipient.get("split", "").strip(),
                            }
                        )
            else:
                valueType = ""
                valueMethod = ""

            if valueType != "lightning" or valueMethod != "keysend":
                value_items = [{}]

            image = channel.find(it("image"))
            if image is not None:
                art_url = image.get("href", "").strip()
            else:
                art_url = ""

            feed_data = {
                "url": link,
                "title": title,
                "description": description,
                "author": author,
                "link": link,
                "language": language,
                "pubDate": pubDate,
                "lastBuildDate": lastBuildDate,
                "art_url": art_url,
            }

            items = channel.findall("item")
            if not items:
                raise errors.ExternalAPIInvalidResponseDataError(
                    "RSS Feed response did not contain any tracks"
                )
            parsed_items = []
            for item in items:
                if item.findtext("title"):
                    title = item.findtext("title").strip()
                elif item.findtext(it("title")):
                    title = item.findtext(it("title")).strip()
                elif item.findtext(pc("title")):
                    title = item.findtext(pc("title")).strip()
                else:
                    title = "Unknown"

                if item.findtext("link"):
                    link = item.findtext("link").strip()
                elif item.findtext(it("link")):
                    link = item.findtext(it("link")).strip()
                elif item.findtext(pc("link")):
                    link = item.findtext(pc("link")).strip()
                else:
                    link = ""

                if item.findtext("guid"):
                    guid = item.findtext("guid").strip()
                elif item.findtext(it("guid")):
                    guid = item.findtext(it("guid")).strip()
                elif item.findtext(pc("guid")):
                    guid = item.findtext(pc("guid")).strip()
                else:
                    guid = ""

                if item.findtext("description"):
                    description = item.findtext("description").strip()
                elif item.findtext(it("description")):
                    description = item.findtext(it("description")).strip()
                elif item.findtext(pc("description")):
                    description = item.findtext(pc("description")).strip()
                else:
                    description = "Unknown"

                if item.findtext("pubDate"):
                    pubDate = item.findtext("pubDate").strip()
                elif item.findtext(it("pubDate")):
                    pubDate = item.findtext(it("pubDate")).strip()
                elif item.findtext(pc("pubDate")):
                    pubDate = item.findtext(pc("pubDate")).strip()
                else:
                    pubDate = "Unknown"

                if item.find("enclosure") is not None:
                    enclosure_url = item.find("enclosure").attrib.get("url", "").strip()
                else:
                    enclosure_url = ""

                if item.find("enclosure") is not None:
                    enclosure_length = (
                        item.find("enclosure").attrib.get("length", "").strip()
                    )
                else:
                    enclosure_length = ""

                if item.find("enclosure") is not None:
                    enclosure_type = (
                        item.find("enclosure").attrib.get("type", "").strip()
                    )
                else:
                    enclosure_type = ""

                image = item.find((it("image")))
                if image is not None:
                    art_url = image.get("href", "").strip()
                else:
                    art_url = ""

                item_data = {
                    "title": title,
                    "link": link,
                    "guid": guid,
                    "description": description,
                    "pubDate": pubDate,
                    "enclosure_url": enclosure_url,
                    "enclosure_length": enclosure_length,
                    "enclosure_type": enclosure_type,
                    "image": art_url,
                }
                parsed_items.append(item_data)

        except ET.ParseError as e:
            raise errors.ExternalAPIBadRequestError(
                f"Failed to parse RSS feed: {str(e)}"
            )

        feed = Rss(
            url=feed_data["url"],
            title=feed_data["title"],
            description=feed_data["description"],
            artist=feed_data["author"],
            link=feed_data["link"],
            art_url=feed_data["art_url"],
            language=feed_data["language"],
            pub_date=feed_data["pubDate"],
            last_build_date=feed_data["lastBuildDate"],
            items=parsed_items,
            value_items=value_items,
        )

        return feed

    @classmethod
    def get_feed_by_url(cls, url: str) -> Rss:
        headers = {
            "User-Agent": identity.get_user_agent()
            or "Mozilla/5.0 (compatible; rss-music-backend/1.0)",
            "Accept": "application/rss+xml, application/xml, text/xml, */*; q=0.1",
        }

        log_request(
            logger,
            "info",
            "external_request_sent",
            "Request sent to RSS feed URL",
            service="RSSFeed",
            url=url,
        )

        try:
            response = requests.get(
                url, headers=headers, timeout=TIMEOUT, allow_redirects=True
            )

            level = "info" if response.status_code < 400 else "warn"
            log_request(
                logger,
                level,
                "external_response_received",
                "Response received from RSS feed URL",
                service="RSSFeed",
                status_code=response.status_code,
            )
        except requests.Timeout:
            log_request(
                logger,
                "error",
                "external_timeout",
                "RSS feed timeout",
                service="RSSFeed",
                url=url,
            )
            raise errors.ExternalAPITimeoutError("Feed")
        except requests.RequestException as e:
            log_request(
                logger,
                "error",
                "external_error",
                "Error fetching RSS feed",
                service="RSSFeed",
                url=url,
                error=str(e),
            )
            raise errors.ExternalAPITransportError(
                "An error occurred while sending a request to the Feed"
            )

        return cls.parse_link_feed_response(response)
