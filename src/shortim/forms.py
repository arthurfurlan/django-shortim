# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _
from django.contrib import messages
from models import ShortURL

class ShortURLForm(forms.ModelForm):

    class Meta:
        model = ShortURL

    def save(self, request, api):
        url = self.cleaned_data['url']
        remote_user = self.cleaned_data['remote_user']
        instance = ShortURL.get_or_create_object(url, remote_user)

        if not api:
            message = _('Woow, your URL was successfully shortened.')
            messages.add_message(request, messages.SUCCESS, message)

        self.instance = instance
        return self.instance
