from marshmallow import Schema, fields


class DeletePlaylistTrackResponse(Schema):
    message = fields.Str(dump_only=True)
    playlist_track_id = fields.Int(dump_only=True)
