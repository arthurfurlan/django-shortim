# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from itertools import product
from datetime import datetime
import string
import math

## set the default shorturl chars
DEFAULT_SHORTURL_CHARS = string.uppercase
DEFAULT_SHORTURL_CHARS += string.lowercase
DEFAULT_SHORTURL_CHARS += string.digits

## allow user to configure a different chars chain
SHORTIM_SHORTURL_CHARS = getattr(settings,
    'SHORTIM_SHORTURL_CHARS', DEFAULT_SHORTURL_CHARS)

class ShortURL(models.Model):

    url = models.URLField('url', max_length=255, db_index=True, verify_exists=False)
    hits = models.IntegerField('hits', default=0, editable=False)
    date = models.DateTimeField('date', auto_now_add=True)
    remote_user = models.IPAddressField('remote user')

    class Meta:
        ordering = ['-id', 'hits']
        verbose_name = _('Short URL')

    def __unicode__(self):
        return self.get_short_full_url()

    @staticmethod
    def get_or_create_object(url, remote_user):

        ## create default instance
        instance = ShortURL(url=url, remote_user=remote_user)

        ## get the domain of the new url
        if url.startswith('http://') or url.startswith('https://'):
            clean_url = url.split('/')[2]
        else:
            clean_url = url
        domain = clean_url.split('/')[0]

        ## check if the user is not trying to create a short url of
        ## this site, avoid url shotening recursion
        current_site = Site.objects.get_current()
        if domain == current_site.domain:
            return instance

        ## it is not a local instance, try to get an existent object
        try:
            instance = ShortURL.objects.get(url=url)
        except ShortURL.DoesNotExist:
            instance.save()

        return instance

    @models.permalink
    def get_absolute_url(self):
        code = SequenceMapper.from_decimal(self.id)
        return ('shorturl_preview', (), {'code':code})

    def get_absolute_full_url(self):
        scheme = getattr(settings, 'SHORTIM_SITE_SCHEME', 'http')
        cur_site = Site.objects.get_current()
        return scheme.lower() + '://' + cur_site.domain \
            + self.get_absolute_url()

    def get_short_url(self):
        code = SequenceMapper.from_decimal(self.id)
        return '/' + code

    def get_short_full_url(self):
        scheme = getattr(settings, 'SHORTIM_SITE_SCHEME', 'http')
        cur_site = Site.objects.get_current()
        return scheme.lower() + '://' + cur_site.domain \
            + self.get_short_url()

class SequenceMapper(object):

    @staticmethod
    def from_decimal(number):
        base = len(SHORTIM_SHORTURL_CHARS)
        code = ''

        ## generate the respective code of the sequence
        index = 1
        while number > 0 and index+1 > 0:
            index = number % base - 1
            code = SHORTIM_SHORTURL_CHARS[index] + code
            number = number / base
            if number > 0 and index < 0:
                number -= 1
                index = 0
        return code

    @staticmethod
    def to_decimal(code):
        base = len(SHORTIM_SHORTURL_CHARS)
        number = 0

        ## calculate the respective number of the code
        for i, c in enumerate(code[::-1]):
            index = SHORTIM_SHORTURL_CHARS.index(c)
            number += base ** i * (index+1)
        return number
