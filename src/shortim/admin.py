# -*- coding: utf-8 -*-

from django.contrib import admin
from models import ShortURL

class ShortURLAdmin(admin.ModelAdmin):
    list_display = ('url', 'remote_user', 'hits', 'date')

admin.site.register(ShortURL, ShortURLAdmin)
