from flask import jsonify
from core import logger

def validate(fields):
    """
    Validate a list of fields. Pass the json object from the request with a list of expected fields.
    :param fields: Tuple of (fieldName, validatorObj).
    :return: { 'validated': 'False', 'errors': ['Validation failed for this reason.', 'And this one.'] }
    """
    #TODO: break this out into shared validation class and write unit tests.

    errors = []

    for (name, validator) in fields:
        if type(validator) is not Validator:
            logger.logSystem('Bad validator specified!', enums.e_log_event_level.critical)
            raise(TypeError)

        if not fields.get(name):
            errors.append(name + ' not specified.')
            continue

        result = validator.test(fields[name])
        if len(result) != 0:
            errors.append(name + ' failed validation: ' + result)
            continue

    return jsonify(validated=True if len(errors) == 0 else False, errors=errors)


class Validator():
    def test(self, value):
        """
        Tests a value against this validator.
        :param value: The value to test.
        :return: Empty string if value passes validation, error message if fails.
        """
        return ''


class IntValidator(Validator):

    def __init__(self, max=None, min=None):
        self._max = max
        self._min = min
        pass

    def test(self, value):
        return ''

class StringValidator(Validator):
    def __init__(self, length=None):
        self._length = length
        pass

    def test(self, value):
        pass

