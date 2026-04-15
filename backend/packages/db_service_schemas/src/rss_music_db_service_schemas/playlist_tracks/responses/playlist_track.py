from marshmallow import Schema, fields


class PlaylistTrackResponse(Schema):
    id = fields.Int(dump_only=True)
    playlist_id = fields.Int(dump_only=True)
    track_url = fields.Url(required=True)
    position = fields.Int(required=True)
    added_at = fields.DateTime(required=True)

    title = fields.Str(allow_none=True)
    audio = fields.Url(allow_none=True)

    artist = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    image = fields.Url(allow_none=True)
    value = fields.Dict(allow_none=True)
