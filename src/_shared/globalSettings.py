import transaction, persistent


class GlobalSettings(persistent.Persistent):
    """These are settings that are accessed through the CuteCasa admin screen."""

    def __init__(self):
        self._yoApiKey = None

    @property
    def yoApiKey(self):
        return self._yoApiKey

    @yoApiKey.setter
    def yoApiKey(self, yoApiKey):
        self._yoApiKey = yoApiKey
        transaction.commit()

