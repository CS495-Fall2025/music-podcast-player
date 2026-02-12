from marshmallow import Schema, fields, validate, validates_schema, ValidationError

import rss_music_common_validators as common_validate


class UserExistsRequest(Schema):
    id = fields.Int(validate=validate.Range(min=0))
    username = fields.Str(
        validate=common_validate.username,
    )
    email = fields.Email()

    @validates_schema
    def validate(self, data, **kwargs) -> None:
        if not (
            data.get("id") is not None or data.get("username") or data.get("email")
        ):
            raise ValidationError("No fields provided to identify user")
