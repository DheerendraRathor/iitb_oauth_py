import json

import requests
from requests.auth import HTTPBasicAuth

from django.utils.translation import ugettext_lazy as _

from .settings import sso_oauth_settings
from .exceptions import TokenExchangeError, UserSendMailAPIRequestError, OAuthError, UserFieldAPIRequestError, \
    InsufficientScopes
from django.utils import timezone
from datetime import timedelta


class Token(object):
    def __init__(self, refresh_token=None, access_token=None, expires_in=None, scope=None, token_type=None,
                 created_on=None, expires_on=None):
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.expires_in = expires_in
        self.scope = scope
        self.token_type = token_type
        if created_on:
            self.created_on = created_on
        else:
            self.created_on = timezone.now()
        if expires_on:
            self.expires_on = expires_on
        else:
            self.expires_on = self.created_on + timedelta(seconds=self.expires_in)

    def has_expired(self):
        return timezone.now() > self.expires_on

    def refresh(self):
        return TokenExchange(refresh_token=self.refresh_token).exchange()


class TokenExchange(object):

    def __init__(self, code=None, refresh_token=None, grant_type=None, redirect_uri=None):
        if not (code or refresh_token):
            raise TokenExchangeError('Provide atleast code or refresh_token')

        if code and refresh_token:
            raise TokenExchangeError('Both code and refresh token should not be provided')

        if code:
            self.code = code
            self.grant_type = 'authorization_code'
        elif refresh_token:
            self.refresh_token = refresh_token
            self.grant_type = 'refresh_token'

        if redirect_uri:
            self.redirect_uri = redirect_uri
        else:
            self.redirect_uri = sso_oauth_settings.DEFAULT_REDIRECT_URI

        if grant_type:
            self.grant_type = grant_type

    def exchange(self):
        request_data = {
            'grant_type': self.grant_type,
        }
        if self.code:
            request_data['code'] = self.code
            request_data['redirect_uri'] = self.redirect_uri
        elif self.refresh_token:
            request_data['refresh_token'] = self.refresh_token
        else:
            raise TokenExchangeError('Neither refresh token nor code is present')
        return TokenExchangeRequest(request_data).execute()


class RequestType(object):
    GET = 'get'
    POST = 'post'


class OAuthRequest(object):
    def __init__(self):
        self.auth = HTTPBasicAuth(sso_oauth_settings.CLIENT_ID, sso_oauth_settings.CLIENT_SECRET)
        self.response = None

    def execute(self):
        raise NotImplementedError('execute method is not implemented')

    def _process_response(self):
        raise NotImplementedError('process response is not implemented')


class TokenExchangeRequest(OAuthRequest):
    url = sso_oauth_settings.get_api_url('TOKEN_URL')

    def __init__(self, data):
        super(TokenExchangeRequest, self).__init__()
        self.data = data

    def execute(self):
        self.response = requests.post(self.url, self.data, auth=self.auth)
        return self._process_response()

    def _process_response(self):
        json_response = self.response.json()
        if not self.response.ok:
            raise TokenExchangeError(message=json_response.get('error', 'Response is not OK'),
                                     response=self.response)
        else:
            scopes = json_response.get('scope').split()
            minimum_scopes = sso_oauth_settings.MINIMUM_SCOPES
            for scope in minimum_scopes:
                if scope not in scopes:
                    raise InsufficientScopes(message=_('%(scope)s is necessary') % {'scope': scope})
            return Token(
                refresh_token=json_response.get('refresh_token'),
                access_token=json_response.get('access_token'),
                expires_in=json_response.get('expires_in'),
                scope=json_response.get('scope'),
                token_type=json_response.get('token_type')
            )


class RevokeTokenRequest(TokenExchangeRequest):
    url = sso_oauth_settings.TOKEN_REVOKE_URL

    def _process_response(self):
        if not self.response.ok:
            raise TokenExchangeError(message=self.response.json().get('error', 'Response is not OK'),
                                     response=self.response)


class APIRequest(object):
    def __init__(self, url=None, method=RequestType.GET, access_token=None, token=None):
        if token:
            self.access_token = token.get_access_token()
            self.token_type = token.token_type
        else:
            self.access_token = access_token
            self.token_type = 'Bearer'

        self.auth = "%s %s" % (self.token_type, self.access_token)
        self.method = method
        self.url = url
        self.kwargs = {
            'method': self.method,
            'url': self.url,
            'headers': {
                'Authorization': self.auth,
            },
        }
        self.response = None

    def _process_reponse(self):
        return self.response


class EmailResponse(object):
    def __init__(self, **kwargs):
        self.message_id = kwargs.get('Message-ID', kwargs.get('message_id'))
        self.status = kwargs.get('status', False)


class UserSendMailAPIRequest(APIRequest):
    def __init__(self, subject=None, message=None, reply_to=None, **kwargs):
        url = kwargs.pop('url', sso_oauth_settings.get_api_url('USER_SEND_MAIL_API_URL'))
        method = kwargs.pop('method', RequestType.POST)
        super(UserSendMailAPIRequest, self).__init__(url=url, method=method, **kwargs)

        self.subject = subject
        self.message = message
        if not reply_to:
            self.reply_to = []
        else:
            self.reply_to = reply_to

    def send(self):
        data = {
            'subject': self.subject,
            'message': self.message,
            'reply_to': self.reply_to,
        }
        json_data = json.dumps(data)
        self.kwargs['data'] = json_data
        self.response = requests.request(**self.kwargs)
        return self._process_reponse()

    def _process_reponse(self):
        json_response = self.response.json()
        if self.response.ok:
            return EmailResponse(**json_response)
        else:
            raise UserSendMailAPIRequestError(message=_('Email sending failed'), response=self.response)


class OAuthObject(object):
    def __init__(self, attr_dict):
        for key, val in attr_dict.items():
            if isinstance(val, (list, tuple)):
                setattr(self, key, [OAuthObject(x) if isinstance(x, dict) else x for x in val])
            else:
                setattr(self, key, OAuthObject(val) if isinstance(val, dict) else val)


class UserFieldAPIRequest(APIRequest):
    field_list = [
        'id',
        'first_name',
        'last_name',
        'profile_picture',
        'email',
        'username',
        'program',
        'contacts',
        'insti_address',
        'secondary_emails',
        'mobile',
        'roll_number',
    ]

    def __init__(self, fields=None, **kwargs):
        url = kwargs.pop('url', sso_oauth_settings.get_api_url('USER_API_URL'))
        super(UserFieldAPIRequest, self).__init__(url=url, **kwargs)

        self.fields = []
        if fields and isinstance(fields, (list, tuple, set)):
            for field in fields:
                if field not in self.field_list:
                    raise OAuthError(message=_('Field %(field)s is not a valid field') % {'field': field})
                self.fields.append(field)
        else:
            self.fields = self.field_list

        self.oauth_user = None

    def get_oauth_user(self, refresh=False):
        if not self.oauth_user or refresh:
            self.oauth_user = None
            self._fetch_oauth_user()
        return self.oauth_user

    def _fetch_oauth_user(self):
        fields_val = ','.join(self.fields)
        query_params = {
            sso_oauth_settings.FIELD_QUERY: fields_val
        }
        self.kwargs['params'] = query_params
        response = requests.request(**self.kwargs)
        json_response = response.json()
        if response.ok:
            self.oauth_user = OAuthObject(json_response)
        else:
            raise UserFieldAPIRequestError(message=_('Got error while fetching user api response'),
                                           response=response)
