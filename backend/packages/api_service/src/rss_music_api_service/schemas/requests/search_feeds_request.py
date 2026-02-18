import re

from marshmallow import Schema, fields, validate

from rss_music_api_service.schemas import SAnd


class SearchFeedsRequestSchema(Schema):
    query = fields.Str(
        required=True,
        validate=SAnd(
            validate.Length(min=1, max=255),
            # Allows input made of letters (including unicode), numbers, and punctuation.
            validate.Regexp(r"^(?!.*--)[\w !'?.-]+$", flags=re.UNICODE),
        ),
    )
    count = fields.Int(load_default=25, validate=validate.Range(min=1, max=50))
    start = fields.Int(load_default=0, validate=validate.Range(min=0))
