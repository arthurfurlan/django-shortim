# -*- coding: utf-8 -*-

from django import template
from django.contrib.sites.models import Site
from shortim.models import ShortURL
register = template.Library()

@register.filter
def shortim_short_url(url):

    ## if is a local address, complete with the domain
    if url.startswith('/'):
        current_site = Site.objects.get_current()
        url = 'http://' + current_site.domain + url
    
    ## get the object and, if it not exists, create one
    remote_user = '127.0.0.1'
    shorturl = ShortURL.get_or_create_object(url, remote_user)
    return shorturl.get_short_full_url()
