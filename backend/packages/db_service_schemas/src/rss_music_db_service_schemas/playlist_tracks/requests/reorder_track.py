from marshmallow import Schema, fields


class ReorderTrackRequest(Schema):
    track_url = fields.Str(required=True)
    new_position = fields.Int(required=True, strict=True)
    created_by_user_id = fields.Int(required=True)
