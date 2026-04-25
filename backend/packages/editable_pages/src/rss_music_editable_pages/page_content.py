"""S3-backed service for reading and writing static page content."""

import json
import os

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


PAGE_KEYS = {
    "about": "pages/about.json",
    "contact": "pages/contact.json",
    "terms": "pages/terms.json",
    "privacy": "pages/privacy.json",
    "cookies": "pages/cookies.json",
}

MAX_CONTENT_BYTES = 64 * 1024  # 64 KB, small for speed/security
DEFAULT_PAGE_VERSION = 0


class PageNotFoundError(Exception):
    pass


class ContentTooLargeError(Exception):
    pass


def _get_client():
    endpoint_url = os.environ.get("RSS_PLAYER_S3_ENDPOINT_URL")
    kwargs = {}
    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url
        kwargs["config"] = Config(s3={"addressing_style": "path"})
    return boto3.client("s3", **kwargs)


def _get_bucket() -> str:
    return os.environ["RSS_PLAYER_CMS_BUCKET"]


def _get_page_object(page: str) -> dict:
    if page not in PAGE_KEYS:
        raise PageNotFoundError(f"Unknown page: {page}")

    s3 = _get_client()
    key = PAGE_KEYS[page]

    try:
        response = s3.get_object(Bucket=_get_bucket(), Key=key)
        body = response["Body"].read()
        return json.loads(body)
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return {
                "html": "",
                "version": DEFAULT_PAGE_VERSION,
            }
        raise


def get_page_content(page: str) -> str:
    """Return the html for the given page name."""
    page_obj = _get_page_object(page)

    return page_obj["html"]


def get_page_version(page: str) -> int:
    """Return the version for the given page name."""
    page_obj = _get_page_object(page)

    return page_obj["version"]


def put_page_content(page: str, html: str, version: int | None = None) -> dict:
    """Store sanitized HTML for the given page name. Returns {"html": <stored>}."""
    if page not in PAGE_KEYS:
        raise PageNotFoundError(f"Unknown page: {page}")

    page_version = version if version is not None else get_page_version(page)
    body = json.dumps(
        {
            "html": html,
            # We do not update the version unless explicitly told to, as it is used to
            # determine when an update to a page in the code should override updates
            # made by an admin.
            "version": page_version,
        }
    ).encode("utf-8")
    if len(body) > MAX_CONTENT_BYTES:
        raise ContentTooLargeError("Content exceeds 64 KB limit")

    s3 = _get_client()
    key = PAGE_KEYS[page]

    s3.put_object(
        Bucket=_get_bucket(),
        Key=key,
        Body=body,
        ContentType="application/json",
    )

    return {
        "html": html,
        "version": page_version,
    }
