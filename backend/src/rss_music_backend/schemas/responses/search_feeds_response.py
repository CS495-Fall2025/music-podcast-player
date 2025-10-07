from enum import Enum, IntEnum
import re

from marshmallow import Schema, fields, validate


class PodcastIndexFeedType:
    RSS = 0
    ATOM = 1

# Defined here: https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/tags/medium.md
class Medium:
    PODCAST = "podcast"
    MUSIC = "music"
    VIDEO = "video"
    FILM = "film"
    AUDIOBOOK = "audiobook"
    NEWSLETTER = "newsletter"
    BLOG = "blog"
    PUBLISHER = "publisher"
    COURSE = "course"

# Description from https://podcastindex-org.github.io/docs-api/#get-/search/music/byterm

class PodcastIndexCategorySchema(Schema):
    # Currently there are 112 categories, but this might change so I've limited this to
    # 200.
    id = fields.Int(required=True, validate=validate.Range(min=1, max=200))

    # The longest is currently 16 characters.
    name = fields.Str(required=True, validate=validate.Length(min=1, max=63))


class PodcastIndexFeedSchema(Schema):
    id = fields.Int(required=True, validate=validate.Range(min=0))
    podcastGuid = fields.UUID(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    url = fields.URL(required=True)
    originalUrl = fields.URL(required=True)
    link = fields.URL(required=True)
    description = fields.Str(min=0, max=4000)
    author = fields.Str(required=True, validate=validate.Length(min=0, max=255))
    ownerName = fields.Str(required=True, validate=validate.Length(min=0, max=255))
    image = fields.URL(required=True)
    artwork = fields.URL(required=True)
    lastUpdateTime = fields.Int(required=True, validate=validate.Range(min=0))
    lastCrawlTime = fields.Int(required=True, validate=validate.Range(min=0))
    lastParseTime = fields.Int(required=True, validate=validate.Range(min=0))
    lastGoodHttpStatusTime = fields.Int(required=True, validate=validate.Range(min=0))
    lastHttpStatus = fields.Int(required=True, validate=validate.Range(min=100, max=999))
    contentType = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    itunesId = fields.Int(required=true, allow_none=True, validate=validate.Range(min=0))
    generator = fields.Str(required=True, validate=validate.Length(min=0, max=255))
    language = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    explicit = fields.Bool(required=True)
    type = fields.Enum(PodcastIndexFeedType, required=True, by_value=True)
    medium = fields.Enum(Medium, required=True, by_value=True)
    dead = fields.Bool(required=True)
    episodeCount = fields.Int(required=True, validate=validate.Range(min=1))
    crawlErrors = fields.Int(required=True, validate=validate.Range(min=0))
    parseErrors = fields.Int(required=True, validate=validate.Range(min=0))
    categories = fields.List(fields.Nested(PodcastIndexCategorySchema), required=True)
    locked = fields.Bool(required=True)
    imageUrlHash = fields.Int(required=True)
    newestItemPubdate = fields.Int(required=true, validate=validate.Range(min=0))


class SearchFeedsResponseSchema(Schema):
    status = fields.Bool(required=True)
    feeds = fields.List(fields.Nested(PodcastIndexFeedSchema), required=True)
    count = fields.Int(required=True, validate=validate.Range(min=0))
    query = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(required=True, validate=validate.Length(min=1, max=255))
