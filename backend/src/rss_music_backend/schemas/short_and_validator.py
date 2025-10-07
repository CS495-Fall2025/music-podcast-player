from marshmallow import Validator


class SAnd(Validator):
    def __init__(self, *validators: Validator):
        self._validators = validators

    def __call__(self, input):
        # Apply each validator in order to the input. If even one fails, we short
        # circuit the validation process.
        for validator in self._validators:
            validator(input)

        return input
