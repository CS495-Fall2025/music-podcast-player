from marshmallow import Schema, fields


class AddTrackToPlaylistRequest(Schema):
    track_url = fields.Str(required=True)
    created_by_user_id = fields.Int(required=True)
