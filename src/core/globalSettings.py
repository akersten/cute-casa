import transaction, persistent


class GlobalSettings(persistent.Persistent):
    """These are settings that are accessed through the CuteCasa admin screen."""

    def __init__(self):
        self._yoApiKey = ""
        self._registrationEnabled = True

    @property
    def yoApiKey(self):
        return self._yoApiKey

    @yoApiKey.setter
    def yoApiKey(self, yoApiKey):
        self._yoApiKey = yoApiKey
        transaction.commit()

    @property
    def registrationEnabled(self):
        return self._registrationEnabled

    @registrationEnabled.setter
    def registrationEnabled(self, value):
        if type(value) is not bool:
            raise TypeError('registrationEnabled is a boolean property.')

        self._registrationEnabled = value
        transaction.commit()