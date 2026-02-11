import re

from marshmallow import validate


username = validate.And(
    validate.Length(min=6, max=30),
    validate.Regexp(r"^[a-zA-Z0-9]\w*[a-zA-Z0-9]$", flags=re.UNICODE),
)


password = validate.And(
    validate.Length(min=12, max=64),
    # Require at least one alphabetical character, digit, and special character.
    validate.Regexp(
        r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).*$",
        flags=re.UNICODE,
    ),
)
