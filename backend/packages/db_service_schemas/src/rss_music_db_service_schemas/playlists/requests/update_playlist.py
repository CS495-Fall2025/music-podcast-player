from marshmallow import Schema, fields

import rss_music_common_validators as common_validate


class UpdatePlaylistRequest(Schema):
    # Playlist ID
    id = fields.Int(required=True)

    title = fields.Str(
        validate=common_validate.Length(min=1, max=100))
    description = fields.Str(
        validate=common_validate.Length(max=500)
    )
