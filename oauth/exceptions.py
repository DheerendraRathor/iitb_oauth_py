
class OAuthError(Exception):

    def __init__(self, message=None, response=None):
        super(OAuthError, self).__init__(message)
        self.response = response


class TokenExchangeError(OAuthError):
    pass


class UserSendMailAPIRequestError(OAuthError):
    pass


class UserFieldAPIRequestError(OAuthError):
    pass


class InvalidAuthorizationError(OAuthError):
    pass


class InsufficientScopes(OAuthError):
    pass
