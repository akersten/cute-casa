import requests

class Yoer:

    def __init__(self, apiKey):
        if (apiKey is None or type(apiKey) is not str):
            raise TypeError('apiKey must be a string.')
        if (len(apiKey) == 0):
            raise ValueError('apiKey must be longer than 0 characters.')

        self.apiKey = apiKey

    def yo(self, target, message):
        """
        Send a Yo to someone.
        :param target: Username to send the Yo to.
        :param message: The message to send. Limited to 30 characters.
        """
        if (target is None or type(target) is not str):
            raise TypeError('target must be a string.')
        if (len(target) == 0):
            raise ValueError('target must be longer than 0 characters.')

        if (message is None or type(message) is not str):
            raise TypeError('message must be a string.')
        if (len(message) == 0):
            raise ValueError('message must be longer than 0 characters.')
        if (len(message) > 30):
            raise ValueError('message cannot be longer than 30 characters.')

        if not self.apiKey == "TEST":
            requests.post("http://api.justyo.co/yo/", data={
                'api_token': self.apiKey,
                'username': target,
                'text': message})


#