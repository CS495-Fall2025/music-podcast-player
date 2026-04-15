from marshmallow import Schema, fields, validate


class CreatePlaylistRequest(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=False, validate=validate.Length(max=255))
    created_by_user_id = fields.Int(required=True)
