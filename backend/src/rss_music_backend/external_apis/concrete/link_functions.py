from marshmallow import ValidationError
import requests

from rss_music_backend.data import Rss
from rss_music_backend.external_apis.auth import identity
from rss_music_backend.external_apis import errors

import xml.etree.ElementTree as ET

TIMEOUT = (3, 10)

class LinkFunctions:
    @classmethod
    def make_link_feed_request(cls, url: str) -> dict:
        request = requests.Request("GET", url)
        return request.prepare()

    @classmethod
    def parse_link_feed_response(cls, response: requests.Response) -> Rss:
        if not response.status_code ==200:
            match response.status_code:
                case 400:
                    raise errors.ExternalAPIBadRequestError(
                        "Recieved 400 bad request from the Link Endpoint"
                    )
                case 401:
                    raise errors.ExternalAPIBadAuthenticationError(
                        "Recieved 401 bad authentication from the Link Endpoint"
                    )
                case _:
                    raise errors.ExternalAPIReturnedError(
                        f"Recieved code {response.status_code} from the Link Endpoint"
                    )
                
        ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
        def it(tag: str) -> str:
            return f"{{{ITUNES_NS}}}{tag}"
        
        try:
            root = ET.fromstring(response.content)
            channel = root.find('channel')
            if channel is None:
                raise errors.ExternalAPIInvalidResponseDataError(
                    "RSS Feed response did not contain data"
                )
            
            title = (channel.findtext('title') or channel.findtext(it('title')) or "").strip()
            description = (channel.findtext('description') or channel.findtext(it('summary')) or "").strip()
            author = (channel.findtext(it('owner')) or channel.findtext(it('owner')) or "").strip()
            link = (channel.findtext('link') or response.url or "").strip()
            language = (channel.findtext('language') or "Unknown").strip()
            pubDate = (channel.findtext('pubDate') or "Unknown").strip()
            lastBuildDate = (channel.findtext('lastBuildDate') or "Unknown").strip()

            
            feed_data = {
                "url": response.url,
                "title": title if title else "No Title",
                "description": description if description else "No Description",
                "author": author if author else "No Author",
                "link": link if link else response.url,
                "language": language if language else "Unknown",
                "pubDate": pubDate if pubDate else "Unknown",
                "lastBuildDate": lastBuildDate if lastBuildDate else "Unknown",
            }

            parsed_image = []
            for parts in channel.findall('image'):
                image_data = {
                    "url": parts.find('url').text,
                    "title": parts.find('title').text,
                    "link": parts.find('link').text,
                }
                parsed_image.append(image_data)

            items = channel.findall('item')
            if not items:
                raise errors.ExternalAPIInvalidResponseDataError(
                    "RSS Feed response did not contain any tracks"
                )
            parsed_items = []
            for item in items:
                title = (item.findtext('title') or "No Title").strip()
                link = (item.findtext('link') or "").strip()
                guid = (item.findtext('guid') or "").strip()
                description = item.findtext('description') or "".strip()
                pubDate = (item.findtext('pubDate')or "Unknown").strip()
                enclosure_url = item.find('enclosure').attrib.get('url', '').strip() if item.find('enclosure') is not None else ""
                enclosure_length = item.find('enclosure').attrib.get('length', '').strip() if item.find('enclosure') is not None else ""
                enclosure_type = item.find('enclosure').attrib.get('type', '').strip() if item.find('enclosure') is not None else ""
                image = item.find(it('image')).attrib.get('href', '').strip() if item.find(it('image')) is not None else ""
                item_data = {
                    "title": title,
                    "link": link,
                    "guid": guid,
                    "description": description,
                    "pubDate": pubDate,
                    "enclosure_url": enclosure_url,
                    "enclosure_length": enclosure_length,
                    "enclosure_type": enclosure_type,
                    "image": image
                }
                parsed_items.append(item_data)

                

        except ValidationError:
            raise errors.ExternalAPIInvalidResponseDataError(
                "Link Endpoint response did not match expected schema"
            )
        
        feed = Rss(
            url=feed_data["url"],
            title=feed_data["title"],
            description=feed_data["description"],
            artist=feed_data["author"],
            link=feed_data["link"],
            art_url=parsed_image[0]["url"] if parsed_image else "",
            language=feed_data["language"],
            pub_date=feed_data["pubDate"],
            last_build_date=feed_data["lastBuildDate"],
            items=parsed_items,
        )

        return feed
    
    @classmethod
    def get_feed_by_url(cls, url: str) -> Rss:
        
        headers = {"User-Agent": identity.get_user_agent() or "Mozilla/5.0 (compatible; rss-music-backend/1.0)",
        "Accept": "application/rss+xml, application/xml, text/xml, */*; q=0.1"}

        try:
            response = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=True)
        except requests.Timeout:
            raise errors.ExternalAPITimeoutError("Feed")
        except requests.RequestException:
            raise errors.ExternalAPITransportError(
                "An error occurred while sending a request to the Feed"
            )

        return cls.parse_link_feed_response(response)