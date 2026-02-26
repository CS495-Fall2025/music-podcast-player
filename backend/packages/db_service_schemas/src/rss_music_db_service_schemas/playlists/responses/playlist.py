from marshmallow import Schema, fields

import rss_music_common_validators as common_validate


class PlaylistResponse(Schema):
    id = fields.Int(dump_only=True)

    title = fields.Str(required=True)
    description = fields.Str()

    created_by_user_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    track_count = fields.Int(dump_only=True)
