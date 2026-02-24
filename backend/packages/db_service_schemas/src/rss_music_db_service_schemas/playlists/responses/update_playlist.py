from marshmallow import Schema, fields

import rss_music_common_validators as common_validate


class UpdatePlaylistResponse(Schema):
    # Playlist ID
    id = fields.Int(dump_only=True)

    title = fields.Str()
    description = fields.Str()
    track_count = fields.Int(dump_only=True)

    updated_at = fields.DateTime(dump_only=True)
