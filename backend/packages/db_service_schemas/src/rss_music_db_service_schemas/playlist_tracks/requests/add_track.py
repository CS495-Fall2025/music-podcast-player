from marshmallow import Schema, fields


class AddTrackToPlaylistRequest(Schema):
    track_url = fields.Str(required=True, schemes={"http", "https"})
