from marshmallow import Schema, fields

import rss_music_common_validators as common_validate


class DeletePlaylistRequest(Schema):
    created_by_user_id = fields.Int(required=True)
