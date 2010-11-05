# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic import create_update, list_detail
from models import ShortURL
import views

## creator view
shortim_create = url(
    r'^$',
    views.create,
    name='shortim_create',
)

## creator view (api version)
shortim_api_create = url(
    r'^api/create/$',
    views.create,
    { 'api':True },
    name='shortim_api_create',
)

## preview view
shortim_preview = url(
    r'^preview/(?P<code>[\w\d]+/)$',
    views.preview,
    name='shortim_preview',
)

## preview view (api version)
shortim_api_preview = url(
    r'^api/preview(/(?P<code>[\w\d]+))?/$',
    views.preview,
    { 'api':True },
    name='shortim_api_preview',
)

## ranking view
shortim_ranking = url(
    r'^ranking/$',
    views.ranking,
    name='shortim_ranking',
)

## redirector view
shortim_redirect = url(
    r'^(?P<code>[A-Z0-9a-z]+)/$',
    views.redirect,
    name='shortim_redirect',
)


## join all the urls created above into a urlpatterns group
urlpatterns = patterns('',
    shortim_create,
    shortim_api_create,
    shortim_preview,
    shortim_api_preview,
    shortim_ranking,
    shortim_redirect,
)
