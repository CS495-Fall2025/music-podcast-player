from marshmallow import Schema, fields


class DeletePlaylistResponse(Schema):
    message = fields.Str(dump_only=True)
    deleted_id = fields.Int(dump_only=True)
