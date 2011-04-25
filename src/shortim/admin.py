# -*- coding: utf-8 -*-

from django.contrib import admin
from models import ShortURL, ShortURLHit

class ShortURLAdmin(admin.ModelAdmin):
    list_display = ('url', 'remote_user', 'date')

admin.site.register(ShortURL, ShortURLAdmin)
admin.site.register(ShortURLHit)
