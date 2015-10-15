from .request import TokenExchange
from .exceptions import InvalidAuthorizationError
from django.utils.translation import ugettext_lazy as _


class Authorization(object):

    def __init__(self, request):
        self._error = request.GET.get('error')
        self._code = request.GET.get('code')

        if self._error:
            raise InvalidAuthorizationError(message=self._error)
        if self._code:
            self._token = TokenExchange(code=self._code).exchange()
        else:
            raise InvalidAuthorizationError(message=_('Neither token nor error is present'))

    def get_token(self):
        try:
            return self._token
        except AttributeError:
            return None