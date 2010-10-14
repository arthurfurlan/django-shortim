# -*- coding: utf-8 -*-

from django.conf import settings

def site(request):
    scheme = getattr(settings, 'SHORTIM_SITE_SCHEME', 'http')
    return { 'SHORTIM_SITE_SCHEME':scheme }
