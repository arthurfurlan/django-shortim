# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from sequencemapper import SequenceMapper
from BeautifulSoup import BeautifulSoup
from pygooglechart import QRChart
from itertools import product
from datetime import datetime, timedelta
from shortim import signals
import httplib
import urllib
import math
import os
import re

## allow user to configure the thumbail size
SHORTIM_THUMBNAIL_SIZE = getattr(settings,
    'SHORTIM_THUMBNAIL_SIZE', 200)

## number of entries displayed in the rankings
SHORTIM_RANKING_SIZE = getattr(settings,
    'SHORTIM_RANKING_SIZE', 10)

## number of times a page can be redirected
SHORTIM_REDIRECT_LIMIT = 10

## api rate limit
SHORTIM_RATELIMIT_MINUTE = getattr(settings,
    'SHORTIM_RATELIMIT_MINUTE', 100)
SHORTIM_RATELIMIT_HOUR = getattr(settings,
    'SHORTIM_RATELIMIT_HOUR', 5000)

## QRCODE Settings
SHORTIM_QRCODE_ENABLED = getattr(settings,
    'SHORTIM_QRCODE_ENABLED', False)
SHORTIM_QRCODE_SIZE = getattr(settings,
    'SHORTIM_QRCODE_SIZE', 100)
SHORTIM_QRCODE_DIR = getattr(settings,
    'SHORTIM_QRCODE_DIR', 'qrcode')
SHORTIM_QRCODE_URL = getattr(settings,
    'SHORTIM_QRCODE_URL', None)


class RedirectLimitError(Exception):
    pass

class ShortURLManager(models.Manager):

    def tt(self, tt_date=None):
        if tt_date:
            queryset = self.filter(hits__date__gte=tt_date)
        else:
            queryset = self
        return queryset.annotate(tt_hits=models.Count('hits')).\
            order_by('-tt_hits', '-date')

    def tt_last_hour(self, ranking_size=SHORTIM_RANKING_SIZE):
        tt_date = datetime.now() - timedelta(hours=1)
        return self.tt(tt_date)[:ranking_size]

    def tt_last_day(self, ranking_size=SHORTIM_RANKING_SIZE):
        tt_date = datetime.now() - timedelta(days=1)
        return self.tt(tt_date)[:ranking_size]

    def tt_last_week(self, ranking_size=SHORTIM_RANKING_SIZE):
        tt_date = datetime.now() - timedelta(weeks=1)
        return self.tt(tt_date)[:ranking_size]

    def tt_last_month(self, ranking_size=SHORTIM_RANKING_SIZE):
        tt_date = datetime.now() - timedelta(days=30)
        return self.tt(tt_date)[:ranking_size]

    def tt_forever(self, ranking_size=SHORTIM_RANKING_SIZE):
        queryset = self.tt()
        if ranking_size:
            return queryset[:ranking_size]
        return queryset

class ShortURL(models.Model):

    url = models.URLField('url', max_length=255, db_index=True, verify_exists=False)
    canonical_url = models.URLField('canonical url', max_length=255,
            null=True, blank=True, default=None, verify_exists=False)
    date = models.DateTimeField('date', auto_now_add=True)
    remote_user = models.IPAddressField('remote user')
    collect_date = models.DateTimeField('collect date', blank=True, null=True, default=None)
    title = models.CharField('title', max_length=255, blank=True, null=True, default=None)
    mime = models.CharField('mime', max_length=100, blank=True, null=True, default=None)

    objects = ShortURLManager()

    class Meta:
        ordering = ['-id']
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
            raise ValidationError(_('Rate limit exceeded.'))

        # hour rate limit
        rate_hour = datetime.now() - timedelta(hours=SHORTIM_RATELIMIT_HOUR)
        hour_count = ShortURL.objects.filter(remote_user=self.remote_user,
                date__gte=rate_hour).count()
        if hour_count >= SHORTIM_RATELIMIT_HOUR:
            raise ValidationError(_('Rate limit exceeded.'))

    def _normalize_html_tag(self, content, max_length=None):
        if not content:
            return ''

        content = u' '.join(map(lambda x: x.strip(), content.splitlines())).strip()

        if max_length is not None:
            return content[:max_length]
        else:
            return content

    def collect_content_info(self):
        html, mime = ShortURL._get_response_html(self.url)

        self.collect_date = datetime.now()
        self.mime = mime

        if not html:
            self.save()
            return

        try:
            soup = BeautifulSoup(html)
        except:
            self.save()
            return

        # get the page title
        if soup.title:
            self.title = self._normalize_html_tag(soup.title.string, 255)

        # get the canonical url
        for link in soup.findAll('link'):
            if link.get('rel') == 'canonical' or link.get('rev') == 'canonical':
                self.canonical_url = self._normalize_html_tag(link.get('href'), 255)

        self.save()

    def get_qrcode_path(self):
        code = SequenceMapper.from_decimal(self.id)
        return os.path.join(settings.MEDIA_ROOT, SHORTIM_QRCODE_DIR, code + '.png')

    def get_qrcode_url(self):
        code = SequenceMapper.from_decimal(self.id)
        if SHORTIM_QRCODE_URL:
            return SHORTIM_QRCODE_URL % code
        else:
            return os.path.join(settings.MEDIA_URL, SHORTIM_QRCODE_DIR, code + '.png')

    def create_qrcode_image(self):
        chart = QRChart(SHORTIM_QRCODE_SIZE, SHORTIM_QRCODE_SIZE)
        chart.add_data(self.get_short_full_url())
        chart.set_ec('L', 0)
        chart.download(self.get_qrcode_path())

    def is_local_url(self):
        domain = self.url.split('/')[2]
        current_site = Site.objects.get_current()
        return current_site.domain == domain

    def count_redirect(self, request):
        shorturl_hit = ShortURLHit(shorturl=self)
        shorturl_hit.remote_user = request.META['REMOTE_ADDR']
        shorturl_hit.save()

    @staticmethod
    def _get_response_html(url, redirect_count=0):
        orig_url = url

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
            return '', ''

        ## if the page redirects to another one, go to recursive
        location = response.getheader('location')
        if location:
            redirect_count += 1  # avoid infinite loops

            url = ShortURL._build_location_url(orig_url, location)
            return ShortURL._get_response_html(url, redirect_count)

        ## if the page does not return an HTML content, return
        content_type = response.getheader('content-type')
        if not content_type or 'text/html' not in content_type:
            return '', content_type

        ## finally, return the HTML response
        return response.read(), content_type

    @staticmethod
    def _build_location_url(url, location):
        if location.startswith('http:') or location.startswith('https://'):
            return location
        elif location.startswith('/'):
            url = url.split('/', 3)
            url = '/'.join(url[:-1])
            return url + location
        else:
            url = re.sub('[^/]+$', '', url)
            return url + location

    @staticmethod
    def get_or_create_object(url, remote_user, canonical=False):

        ## it is not a local instance, try to get an existent object
        try:
            instance = ShortURL.objects.get(url=url)
        except ShortURL.DoesNotExist:
            instance = ShortURL(url=url, remote_user=remote_user)

        if instance.is_local_url():
            return instance

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
        except:
            return ''

        for link in soup.findAll('link'):
            if link.get('rel') == 'canonical' or link.get('rev') == 'canonical':
                return link.get('href')

        return ''

    @staticmethod
    def get_content_title(url):

        ## get the html content
        html = ShortURL._get_response_html(url)
        if not html:
            return ''

        try:
            soup = BeautifulSoup(html)
        except:
            return ''

        return soup.title.string


    def get_thumbnail_tag(self):
        api = 'http://api.thumbalizr.com/?url=%s&width=%d'
        url = api % (urllib.quote(self.url), SHORTIM_THUMBNAIL_SIZE)
        return '<img src="%s" />' % url

    @models.permalink
    def get_absolute_url(self):
        if not self.id and self.is_local_url():
            return self.url

        code = SequenceMapper.from_decimal(self.id)
        return ('shortim_preview', (), {'code':code})

    def get_absolute_full_url(self):
        if not self.id and self.is_local_url():
            return self.url

        scheme = getattr(settings, 'SHORTIM_SITE_SCHEME', 'http')
        cur_site = Site.objects.get_current()
        return scheme.lower() + '://' + cur_site.domain \
            + self.get_absolute_url()

    def get_short_url(self):
        code = SequenceMapper.from_decimal(self.id)
        return '/' + code

    def get_short_full_url(self):
        if not self.id and self.is_local_url():
            return self.url

        scheme = getattr(settings, 'SHORTIM_SITE_SCHEME', 'http')
        cur_site = Site.objects.get_current()
        return scheme.lower() + '://' + cur_site.domain \
            + self.get_short_url()

class ShortURLHit(models.Model):

    shorturl = models.ForeignKey(ShortURL, related_name='hits')
    date = models.DateTimeField('date', auto_now_add=True)
    remote_user = models.IPAddressField('remote user')

    class Meta:
        ordering = ['-date']
        verbose_name = _('Short URL Hits')
       
    def __unicode__(self):
        return self.shorturl.get_short_full_url() + \
            self.date.strftime(' - %Y-%m-%d %T')

models.signals.post_save.connect(signals.create_qrcode_image, sender=ShortURL)
