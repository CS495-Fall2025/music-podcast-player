"""Blueprint for GET/PUT static page content stored in S3."""

import bleach
from flask import Blueprint, request

from rss_music_api_service.auth.current_user import (
    get_current_user_is_admin,
)
from rss_music_api_service.routes.auth import login_required
from rss_music_api_service.errors import RequestError, get_error_response
from rss_music_editable_pages.page_content import (
    get_page_content,
    put_page_content,
    PageNotFoundError,
    ContentTooLargeError,
)

PAGES_BP = Blueprint("pages", __name__, url_prefix="/pages")

ALLOWED_TAGS = [
    "p",
    "br",
    "a",
    "strong",
    "b",
    "em",
    "i",
    "ul",
    "ol",
    "li",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
]
ALLOWED_ATTRS = {"a": ["href", "target"]}


@PAGES_BP.get("/<page>")
def get_page(page: str):
    """Public endpoint — returns stored HTML for a page."""
    try:
        data = {"html": get_page_content(page)}
    except PageNotFoundError:
        return get_error_response(RequestError.NOT_FOUND)

    return {"page": page, "html": data["html"]}, 200


@PAGES_BP.put("/<page>")
@login_required
def put_page(page: str):
    """Admin-only endpoint — stores sanitized HTML for a page."""
    if not get_current_user_is_admin():
        return get_error_response(RequestError.FORBIDDEN)

    body = request.get_json(silent=True)
    if body is None or "html" not in body:
        return get_error_response(RequestError.INVALID_FORMAT)

    raw_html: str = body["html"]
    clean_html = bleach.clean(
        raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True
    )

    try:
        result = put_page_content(page, clean_html)
    except PageNotFoundError:
        return get_error_response(RequestError.NOT_FOUND)
    except ContentTooLargeError:
        return get_error_response(RequestError.CONTENT_TOO_LARGE)

    return {"page": page, "html": result["html"]}, 200
