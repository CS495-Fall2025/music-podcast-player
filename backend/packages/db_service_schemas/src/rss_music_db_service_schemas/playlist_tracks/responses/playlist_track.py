from marshmallow import Schema, fields


class PlaylistTrackResponse(Schema):
    playlist_track_id = fields.Int(attribute="id")
    track_url = fields.Url(required=True)
    position = fields.Int(required=True)
    added_at = fields.DateTime(required=True)

    title = fields.Str(required=True)
    audio = fields.Url(required=True)

    artist = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    image = fields.Url(allow_none=True)
    value = fields.Dict(allow_none=True)
