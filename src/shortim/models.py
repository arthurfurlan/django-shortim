# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from BeautifulSoup import BeautifulSoup, HTMLParseError
from itertools import product
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
import httplib
import urllib
import string
import math

## set the default shorturl chars
DEFAULT_SHORTURL_CHARS = string.uppercase
DEFAULT_SHORTURL_CHARS += string.lowercase
DEFAULT_SHORTURL_CHARS += string.digits

## allow user to configure a different chars chain
SHORTIM_SHORTURL_CHARS = getattr(settings,
    'SHORTIM_SHORTURL_CHARS', DEFAULT_SHORTURL_CHARS)

## allow user to configure the thumbail size
SHORTIM_THUMBNAIL_SIZE = getattr(settings,
    'SHORTIM_THUMBNAIL_SIZE', 200)

## number of times a page can be redirected
SHORTIM_REDIRECT_LIMIT = 10

## api rate limit
SHORTIM_RATELIMIT_MINUTE = getattr(settings,
    'SHORTIM_RATELIMIT_MINUTE', 100)
SHORTIM_RATELIMIT_HOUR = getattr(settings,
    'SHORTIM_RATELIMIT_HOUR', 5000)

class RedirectLimitError(Exception):
    pass

class ShortURL(models.Model):

    url = models.URLField('url', max_length=255, db_index=True, verify_exists=False)
    canonical_url = models.URLField('canonical url', max_length=255,
            null=True, blank=True, default=None, verify_exists=False)
    hits = models.IntegerField('hits', default=0, editable=False)
    date = models.DateTimeField('date', auto_now_add=True)
    remote_user = models.IPAddressField('remote user')

    class Meta:
        ordering = ['-id', 'hits']
        verbose_name = _('Short URL')

    def __unicode__(self):
        return self.get_short_full_url()

    def clean(self):

        # if the object is being created, check the rate limits
        if self.pk:
            return

        # minute rate limit
        rate_minute = datetime.now() - timedelta(minutes=SHORTIM_RATELIMIT_MINUTE)
        minute_count = ShortURL.objects.filter(remote_user=self.remote_user,
                date__gte=rate_minute).count()
        if minute_count >= SHORTIM_RATELIMIT_MINUTE:
            raise ValidationError(_('Rate limite exceeded.'))

        # hour rate limit
        rate_hour = datetime.now() - timedelta(hours=SHORTIM_RATELIMIT_HOUR)
        hour_count = ShortURL.objects.filter(remote_user=self.remote_user,
                date__gte=rate_hour).count()
        if hour_count >= SHORTIM_RATELIMIT_HOUR:
            raise ValidationError(_('Rate limit exceeded.'))

    @staticmethod
    def _get_response_html(url, redirect_count=0):

        ## check if the limit was reached
        if redirect_count >= SHORTIM_REDIRECT_LIMIT:
            raise RedirectLimitError('Redirection limit reached.')

        ## remove the protocol part and set the port based on it
        server_port = 80
        if url.startswith('http:') or url.startswith('https:'):
            pieces = url.split('/')
            if pieces[0] == 'https:':
                server_port = 443

            url = '/'.join(pieces[2:])
            if '/' not in url:
                url += '/'

        ## extract server address and server path
        try:
           server_addr, server_path = url.split('/', 1)
        except ValueError:
           server_addr = url
           server_path = ''
        server_path = '/' + server_path

        ## get the server port from "domain:port" urls
        try:
            server_addr, server_port = server_addr.split(':')
        except ValueError:
            pass

        ## start an HTTP connection
        try:
            conn = httplib.HTTPConnection(server_addr, server_port)
            conn.request("GET", server_path)
            response = conn.getresponse()
        except:
            return ''

        ## if the page redirects to another one, go to recursive
        location = response.getheader('location')
        if location:
            redirect_count += 1  # avoid infinite loops
            return ShortURL._get_response_html(location, redirect_count)

        ## if the page does not return an HTML content, return
        content_type = response.getheader('content-type')
        if 'text/html' not in content_type:
            return ''

        ## finally, return the HTML response
        return response.read()

    @staticmethod
    def get_or_create_object(url, remote_user, canonical=False):

        ## it is not a local instance, try to get an existent object
        try:
            instance = ShortURL.objects.get(url=url)
        except ShortURL.DoesNotExist:
            instance = ShortURL(url=url, remote_user=remote_user)

        ## get the canonical_url of the page
        if canonical and instance.canonical_url is None:
            instance.canonical_url = ShortURL.get_canonical_url(url)
            instance.save()

        ## if the instance is not saved yet, save it
        if not instance.pk:
            instance.save()

        return instance

    @staticmethod
    def get_canonical_url(url):

        ## find the canonical url
        html = ShortURL._get_response_html(url)
        if not html:
            return ''

        try:
            soup = BeautifulSoup(html)
        except HTMLParseError:
            return ''

        for link in soup.findAll('link'):
            if link.get('rel') == 'canonical' or link.get('rev') == 'canonical':
                return link.get('href')

        return ''

    def get_thumbnail_tag(self):
        api = 'http://api.thumbalizr.com/?url=%s&width=%d'
        url = api % (urllib.quote(self.url), SHORTIM_THUMBNAIL_SIZE)
        return '<img src="%s" />' % url

    @models.permalink
    def get_absolute_url(self):
        code = SequenceMapper.from_decimal(self.id)
        return ('shortim_preview', (), {'code':code})

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
