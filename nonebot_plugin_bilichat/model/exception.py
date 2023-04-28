class AbortError(Exception):
    def __init__(self, message):
        self.message = message


class BaseBingChatException(Exception):
    pass


class BingChatUnknownException(BaseBingChatException):
    pass


class BingchatNetworkException(BaseBingChatException):
    pass


class BingChatResponseException(BingchatNetworkException):
    pass


class BingChatInvalidSessionException(BingChatResponseException):
    pass


class BingChatAccountReachLimitException(BingChatResponseException):
    pass
