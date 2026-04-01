from marshmallow import Schema, fields, validate


class UpdatePlaylistRequest(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=255))
    created_by_user_id = fields.Int(required=True)
