# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse
from models import ShortURL

DEFAULT_SITE_DOMAIN = 'example.com'

def change_site_domain(sender, **kwargs):

    if not kwargs.get('interactive'):
        return

    ## check if the domain was not configured yet
    current_site = sender.Site.objects.get_current()
    if current_site.domain != DEFAULT_SITE_DOMAIN:
        return

    ## check if the user wants to configure the site
    print '\nThe current site domain is "%s".' % current_site.domain
    prompt = 'Would you like to change it? [y/n] '
    option = ''
    while option.lower() != 'y':
        option = raw_input(prompt)
        if option.lower() == 'n':
            return

    ## get the new site domain
    answer = ''
    prompt = 'Site domain: '
    while not answer:
        answer = raw_input(prompt)
    current_site.domain = answer

    ## get the new site name
    prompt = 'Site name: [%s] ' % current_site.domain
    answer = raw_input(prompt)
    current_site.name = answer or current_site.name

    current_site.save()
    print 'Current site configured.\n'

def create_first_shorturl(sender, **kwargs):

    if not kwargs.get('interactive'):
        return

    ## check if the database contains some URL
    if ShortURL.objects.count() > 0:
        return

    ## check if the user wants to configure the site
    prompt = 'Would you like to create the first URL pointing to this site? [y/n] '
    option = ''
    while option.lower() != 'y':
        option = raw_input(prompt)
        if option.lower() == 'n':
            return

    ## create the first url
    current_site = sender.Site.objects.get_current()
    scheme = getattr(settings, 'SHORTIM_SITE_SCHEME', 'http')
    url = scheme.lower() + '://' + current_site.domain \
            + reverse('shorturl_create')
    shorturl = ShortURL(url=url, remote_user='127.0.0.1')
    shorturl.save()

    print 'First URL created.\n'
