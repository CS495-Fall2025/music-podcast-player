import hashlib
import json
from typing import Callable
import uuid

from requests import PreparedRequest, Response
from urllib.parse import urlparse, parse_qs


# def inspect_url(request: PreparedRequest) -> None:
#    parsed_url = urlparse(request.url)
#    url = urlunparse(parsed_url._replace(query=""))

#    assert "https://api.podcastindex.org/api/1.0/search/music/byterm" == url, (
#        "Request was made to to the wrong url"
#    )


def generate_valid_response(request: PreparedRequest) -> Response:
    parsed_url = urlparse(request.url)
    queries = parse_qs(parsed_url.query)

    max = int(queries["max"][0]) if "max" in queries else 1000

    return generate_limited_response(request, max)


def generate_custom_response(
    request: PreparedRequest, field_modifier: Callable[[dict], dict]
) -> Response:
    parsed_url = urlparse(request.url)
    queries = parse_qs(parsed_url.query)

    max = int(queries["max"][0]) if "max" in queries else 1000
    query = queries["q"][0]

    data = _generate_limited_response_json(query, max)
    field_modifier(data)

    sdata = json.dumps(data)

    response = Response()
    response.status_code = 200
    response._content = sdata.encode("UTF-8")
    response.headers = {"Content-Type": "application/json"}

    return response


def generate_limited_response(request: PreparedRequest, amount: int) -> Response:
    parsed_url = urlparse(request.url)
    queries = parse_qs(parsed_url.query)

    query = queries["q"][0]

    data = _generate_limited_response_json(query, amount)

    sdata = json.dumps(data)

    response = Response()
    response.status_code = 200
    response._content = sdata.encode("UTF-8")
    response.headers = {"Content-Type": "application/json"}

    return response


def generate_bad_request_response(request: PreparedRequest) -> Response:
    data = {
        "status": "false",
        "description": "Error because of bad request",
    }

    sdata = json.dumps(data)

    response = Response()
    response.status_code = 400
    response._content = sdata.encode("UTF-8")
    response.headers = {"Content-Type": "application/json"}

    return response


def generate_bad_authentication_response(request: PreparedRequest) -> Response:
    response = Response()
    response.status_code = 400
    response._content = b"Not authenticated"

    return response


def _generate_limited_response_json(query: str, amount: int) -> dict:
    feeds = []

    for i in range(amount):
        feeds.append(
            {
                "id": i,
                "podcastGuid": str(uuid.uuid4()),
                "title": f"title{i}",
                "url": f"https://rss.net/feed{i}",
                "originalUrl": f"https://rss.net/original/feed{i}",
                "link": f"https://website{i}.net",
                "description": f"Description for {i}",
                "author": f"artist{i}",
                "ownerName": f"feed owner{i}",
                "image": f"https://image.net/feed{i}",
                "artwork": f"https://image.net/artwork/feed{i}",
                "lastUpdateTime": 1000000 + i,
                "lastCrawlTime": 1000001 + i,
                "lastParseTime": 1000002 + i,
                "inPollingQueue": 0,
                "priority": 0,
                "lastGoodHttpStatusTime": 1000003 + i,
                "lastHttpStatus": 200,
                "contentType": "",
                "itunesId": 1 + i,
                "generator": f"generator{i}",
                "language": "",
                "explicit": 0,
                "type": 0,
                "medium": "music",
                "dead": 0,
                "episodeCount": 1 + (i % 3),
                "crawlErrors": 0,
                "parseErrors": 0,
                "categories": {"3": "Cool"},
                "locked": 0,
                "imageUrlHash": int(
                    hashlib.sha1(
                        f"https://image.net/artwork/feed{i}".encode("UTF-8")
                    ).hexdigest(),
                    16,
                ),
                "newestItemPubdate": 1000004 + i,
            }
        )

    data = {
        "status": "true",
        "feeds": feeds,
        "count": amount,
        "query": query,
        "description": f"Feeds matching query {query}",
    }

    return data
