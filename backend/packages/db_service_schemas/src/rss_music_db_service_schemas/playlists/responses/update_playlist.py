from marshmallow import Schema, fields


class UpdatePlaylistResponse(Schema):
    # Playlist ID
    id = fields.Int()

    title = fields.Str()
    description = fields.Str()
    track_count = fields.Int()

    updated_at = fields.DateTime()
