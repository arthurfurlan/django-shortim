# -*- coding: utf-8 -*-

from os import path
from socket import getfqdn

## main settings
SITE_ID = 1
PROJ_DIR = path.abspath(path.dirname(__file__))
ROOT_URLCONF = 'projexample.urls'
SECRET_KEY = 'j#d(7)68vwjj7u6&1347zva(i7uzx1pwq+p@1=0c#*9536-*3+'

## debugging settings
PROD_SERVER = 'prodction.example.com'
DEBUG = (PROD_SERVER != getfqdn())
TEMPLATE_DEBUG = DEBUG

## who'll receive the system emails?
ADMINS = ()
MANAGERS = ADMINS

## database of the project, sqlite by default
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'projexample.sqlite',
    }
}

## l10n e i18n settings
TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True

## paths and urls settings
MEDIA_ROOT = path.join(PROJ_DIR, 'media')
MEDIA_URL = 'http://media.example.cm'
ADMIN_MEDIA_PREFIX = '/media/'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
TEMPLATE_DIRS = (
    path.join(PROJ_DIR, 'templates'),
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'shortim',
)


## load the local settings of the project
try:
    local_settings = path.join(PROJ_DIR, 'local_settings.py')
    execfile(local_settings)
except IOError:
    pass
