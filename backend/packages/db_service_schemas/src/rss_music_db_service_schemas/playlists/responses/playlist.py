from marshmallow import Schema, fields

from rss_music_db_service_schemas.playlist_tracks.responses.playlist_track import (
    PlaylistTrackResponse,
)


class PlaylistResponse(Schema):
    id = fields.Int(dump_only=True)

    title = fields.Str(required=True)
    description = fields.Str()

    created_by_user_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    track_count = fields.Int(dump_only=True)

    tracks = fields.List(fields.Nested(PlaylistTrackResponse), dump_default=[])
