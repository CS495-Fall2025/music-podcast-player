from marshmallow import Schema, fields


class DeletePlaylistRequest(Schema):
    created_by_user_id = fields.Int(required=True)
