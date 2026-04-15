from marshmallow import Schema, fields


class AddTrackToPlaylistRequest(Schema):
    track_url = fields.Str(required=True)
    feed_url = fields.Str(load_default=None)
    created_by_user_id = fields.Int(required=True)
