class TimeoutVerifyException(Exception):
    def __init__(self, message):
        self.message = message

class AuthVerifyException(Exception):
    def __init__(self, message):
        self.message = message
