from marshmallow import Schema, fields, validate

class LinkFeedRequestSchema(Schema):
    url = fields.URL(
        required=True,
        validate=validate.Length(min=1, max=2048),
    )
    