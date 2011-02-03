# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from shortim import signals


class Command(BaseCommand):
    help = 'Used to upload links to 301works.org'

    def handle(self, *args, **options):
        signals.upload_301works()
