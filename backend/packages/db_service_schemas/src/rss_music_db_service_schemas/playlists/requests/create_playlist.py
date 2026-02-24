from marshmallow import Schema, fields

import rss_music_common_validators as common_validate


class CreatePlaylistRequest(Schema):
    title = fields.Str(
        required=True,
        validate=common_validate.Length(min=1, max=100))
    description = fields.Str(
        required=False,
        validate=common_validate.Length(max=500)
    )
