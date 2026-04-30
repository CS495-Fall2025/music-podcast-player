from enum import Enum, IntEnum

from marshmallow import EXCLUDE, Schema, ValidationError, fields, validate, post_load


class PodcastIndexFeedType(IntEnum):
    RSS = 0
    ATOM = 1


# Defined here: https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/tags/medium.md
class Medium(Enum):
    PODCAST = "podcast"
    MUSIC = "music"
    VIDEO = "video"
    FILM = "film"
    AUDIOBOOK = "audiobook"
    NEWSLETTER = "newsletter"
    BLOG = "blog"
    PUBLISHER = "publisher"
    COURSE = "course"


# Reusable validation functions
def validate_url_or_empty(value: str, **kwargs) -> None:
    if value == "":
        return
    validate.URL()(value)


# From https://podcastindex-org.github.io/docs-api/#get-/podcasts/byfeedurl
# Not described in the response for searching music feeds, but shows up anyways.
class FeedFundingSchema(Schema):
    url = fields.URL(required=True, allow_none=True)
    message = fields.Str(required=True, validate=validate.Length(min=1, max=255))


# Description from https://podcastindex-org.github.io/docs-api/#get-/search/music/byterm
class PodcastIndexFeedSchema(Schema):
    id = fields.Int(required=True, validate=validate.Range(min=0))
    podcastGuid = fields.UUID(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    url = fields.URL(required=True)
    originalUrl = fields.Str(required=True, validate=validate_url_or_empty)
    link = fields.String(required=True, validate=validate_url_or_empty)
    description = fields.Str(required=True, validate=validate.Length(min=0, max=4000))
    author = fields.Str(required=True, validate=validate.Length(min=0, max=255))
    ownerName = fields.Str(required=True, validate=validate.Length(min=0, max=255))
    image = fields.Str(required=True, validate=validate_url_or_empty)
    artwork = fields.Str(required=True, validate=validate_url_or_empty)
    lastUpdateTime = fields.Int(required=True, validate=validate.Range(min=0))
    lastCrawlTime = fields.Int(required=True, validate=validate.Range(min=0))
    lastParseTime = fields.Int(required=True, validate=validate.Range(min=0))

    # These were not documented to be here, but are anyways. There are documented in the
    # response here: https://podcastindex-org.github.io/docs-api/#post-/podcasts/batch/byguid
    inPollingQueue = fields.Bool(required=True, allow_none=True)
    priority = fields.Int(required=True, validate=validate.Range(min=-1, max=5))

    lastGoodHttpStatusTime = fields.Int(required=True, validate=validate.Range(min=0))
    lastHttpStatus = fields.Int(
        required=True, validate=validate.Range(min=100, max=999)
    )
    contentType = fields.Str(required=True, validate=validate.Length(min=0, max=255))
    itunesId = fields.Int(
        required=True, allow_none=True, validate=validate.Range(min=0)
    )
    generator = fields.Str(required=True, validate=validate.Length(min=0, max=255))
    language = fields.Str(required=True, validate=validate.Length(min=0, max=255))
    explicit = fields.Bool(required=True)
    type = fields.Enum(PodcastIndexFeedType, required=True, by_value=True)
    medium = fields.Enum(Medium, required=True, by_value=True)
    dead = fields.Bool(required=True)
    episodeCount = fields.Int(required=True, validate=validate.Range(min=1))
    crawlErrors = fields.Int(required=True, validate=validate.Range(min=0))
    parseErrors = fields.Int(required=True, validate=validate.Range(min=0))
    categories = fields.Dict(
        required=True,
        allow_none=True,
        # Currently there are 112 categories, but this might change so I've limited
        # this to 200. The longest is 16 characters.
        keys=fields.Int(required=True, validate=validate.Range(min=0, max=200)),
        values=fields.Str(required=True, validate=validate.Length(min=1, max=63)),
    )
    locked = fields.Bool(required=True)
    imageUrlHash = fields.Int(required=True)
    newestItemPubdate = fields.Int(required=True, validate=validate.Range(min=0))
    funding = fields.Nested(FeedFundingSchema)


class SearchFeedsResponseSchema(Schema):
    status = fields.Bool(required=True)
    feeds = fields.List(fields.Raw(), required=True)
    count = fields.Int(required=True, validate=validate.Range(min=0))
    query = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(required=True, validate=validate.Length(min=1, max=255))

    class Meta:
        # Don't error over extra data in a schema, but remove it.
        unknown = EXCLUDE

    # Any feeds that fail validation are exluded, but don't cause a ValidationError.
    @post_load
    def validate_feeds(self, data, **kwargs):
        valid_feeds = []
        invalid_feeds = {}
        for index, feed in enumerate(data["feeds"]):
            try:
                valid_feed = PodcastIndexFeedSchema().load(feed)
                valid_feeds.append(valid_feed)
            except ValidationError as error:
                invalid_feeds[index] = error.messages

        data["feeds"] = valid_feeds

        # Currently, these are just ignored, but we could log them later.
        data["rejected_feeds"] = invalid_feeds

        return data
