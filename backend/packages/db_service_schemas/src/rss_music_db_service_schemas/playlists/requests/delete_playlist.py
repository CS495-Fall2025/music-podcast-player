from marshmallow import Schema, fields

import rss_music_common_validators as common_validate


class DeletePlaylistRequest(Schema):
    # Only requires playlist id
    id = fields.Int(required=True)
