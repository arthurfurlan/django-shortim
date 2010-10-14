# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic import create_update, list_detail
from models import ShortURL
import views

## creator view
shorturl_create = url(
    r'^$',
    views.create,
    name='shorturl_create',
)

## creator view (api version)
shorturl_api_create = url(
    r'^api/create$',
    views.create,
    { 'api':True },
    name='shorturl_api_create',
)

## preview view
shorturl_preview = url(
    r'^preview/(?P<code>[\w\d]+)/$',
    views.preview,
    name='shorturl_preview',
)

## preview view (api version)
shorturl_api_preview = url(
    r'^api/preview(/(?P<code>[\w\d]+))?/$',
    views.preview,
    { 'api':True },
    name='shorturl_api_preview',
)

## ranking view
shorturl_ranking = url(
    r'^top-10/$',
    views.ranking,
    { 'num_elements':10 },
    name='shorturl_ranking',
)

## redirector view
shorturl_redirect = url(
    r'^(?P<code>[A-Z0-9a-z]+)/$',
    views.redirect,
    name='shorturl_redirect',
)


## join all the urls created above into a urlpatterns group
urlpatterns = patterns('',
    shorturl_create,
    shorturl_api_create,
    shorturl_preview,
    shorturl_api_preview,
    shorturl_ranking,
    shorturl_redirect,
)
