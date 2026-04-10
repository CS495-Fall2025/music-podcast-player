from marshmallow import Schema, fields


class AddTrackToPlaylistRequest(Schema):
    track_url = fields.Str(required=True)
    title = fields.Str(load_default="")
    artist = fields.Str(load_default="")
    description = fields.Str(load_default="")
    audio = fields.Str(load_default="")
    image = fields.Str(load_default="")
    created_by_user_id = fields.Int(required=True)