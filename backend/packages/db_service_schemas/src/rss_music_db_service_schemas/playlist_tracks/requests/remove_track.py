from marshmallow import Schema, fields


class RemoveTrackFromPlaylistRequest(Schema):
    track_url = fields.Str(required=True)
    created_by_user_id = fields.Int(required=True)
