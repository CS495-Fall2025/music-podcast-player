from marshmallow import Schema, fields

import rss_music_common_validators as common_validate


class UpdatePlaylistRequest(Schema):
    title = fields.Str(
        validate=common_validate.Length(min=1, max=100))
    description = fields.Str(
        validate=common_validate.Length(max=255)
    )
    created_by_user_id = fields.Int(required=True)
