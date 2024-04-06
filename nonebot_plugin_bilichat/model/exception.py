class AbortError(Exception):
    """通常情况下是由外部因素（如风控）导致，不影响其余任务执行的异常"""

    def __init__(self, message):
        self.message = message


class CaptchaAbortError(AbortError):
    """由于风控导致需要验证码的异常"""
    def __init__(self, message):
        self.message = message


class NotFindAbortError(AbortError):
    """未找到指定资源的异常"""
    def __init__(self, message):
        self.message = message


class ProssesError(Exception):
    """处理时的异常，通常由于环境错误导致"""
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
