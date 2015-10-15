from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _
from urlparse import urljoin


DEFAULT_APP_SETTINGS = {
    'OAUTH_BASE_URL': 'http://gymkhana.iitb.ac.in/sso/',
    'MINIMUM_SCOPES': [

    ],
    'DEFAULT_FIELDS': [
        'id',
    ],
    'TOKEN_URL': 'oauth/token/',
    'TOKEN_REVOKE_URL': 'oauth/revoke_token/',
    'DEFAULT_REDIRECT_URI': '',
    'USER_API_URL': 'user/api/user',
    'USER_SEND_MAIL_API_URL': 'user/api/send_mail/',
    'FIELD_QUERY': 'fields',
}


class LazySettings(object):

    def __getattr__(self, item):
        attr = getattr(settings, item, None)
        if not attr:
            attr = DEFAULT_APP_SETTINGS.get(item)
        return attr

    def get_api_url(self, item):
        base_url = self.OAUTH_BASE_URL
        if not base_url:
            raise ImproperlyConfigured(_('API Base URL is not present.'
                                         'Please do the same by adding OAUTH_BASE_URL in your settings.py'))
        else:
            item_url = getattr(self, item)
            if not item_url:
                raise ImproperlyConfigured(_('API URL for %(item)s is not configured') % {'item': item})
            else:
                return urljoin(base_url, item_url)


sso_oauth_settings = LazySettings()
