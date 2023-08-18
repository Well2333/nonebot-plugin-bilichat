class AbortError(Exception):
    def __init__(self, message):
        self.message = message


class CaptchaAbortError(AbortError):
    def __init__(self, message):
        self.message = message


class NotFindAbortError(AbortError):
    def __init__(self, message):
        self.message = message


# ===== BING EXCEPTION =====


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


class BingCaptchaException(BingChatResponseException):
    pass
