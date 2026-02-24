from marshmallow import Schema, fields

import rss_music_common_validators as common_validate


class DeletePlaylistResponse(Schema):
    message = fields.Str(dump_only=True)
    deleted_id = fields.Int(dump_only=True)
