try:
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone

from django.db import models
from django.contrib.auth.models import User
from .request import Token


class OAuthToken(models.Model):
    user = models.OneToOneField(User, related_name='token')
    refresh_token = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=16)
    scope = models.TextField()
    expires_in = models.IntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    refresh_on = models.DateTimeField(auto_now=True)

    def get_access_token(self):
        token = Token(refresh_token=self.refresh_token,
                      access_token=self.access_token,
                      expires_in=self.expires_in,
                      scope=self.scope,
                      token_type=self.token_type,
                      created_on=self.refresh_on)
        if token.has_expired():
            token = token.refresh()
            self.refresh_token = token.refresh_token
            self.access_token = token.access_token
            self.expires_in = token.expires_in
            self.token_type = token.token_type
            self.save()
        return self.access_token
