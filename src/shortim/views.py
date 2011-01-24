# -*- coding: utf-8 -*-

from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import list_detail, create_update
from models import ShortURL, SequenceMapper
from forms import ShortURLForm
import json


def _api_response(response_text, response_type=None):
    if response_type == 'json':
        response_text = json.dumps(response_text)
    return HttpResponse(response_text)

def create(request, api=False, template_name=None):

    ## process or display the form based on the request method
    if request.method == 'POST' or api is True:

        ## include the remote address int the submitted data
        data = getattr(request, request.method).copy()
        data['remote_user'] = request.META['REMOTE_ADDR']

        ## validate and process the form
        form = ShortURLForm(data)
        if form.is_valid():
            form.save(request, api)
            instance = form.instance

            ## if page is being accessed as API, return clean data
            if api is True:
                response = ''
                if request.GET.get('canonical') == '1':
                    response = instance.canonical_url
                if not response:
                    response = instance.get_short_full_url()
                return _api_response(response, data.get('type'))

            ## redirect to the preview page
            return HttpResponseRedirect(instance.get_absolute_url())

        ## form is not valid and the page is being accessed as API
        elif api is True:
            return _api_response('ERROR: Invalid data.')

    ## the page was not requested as POST neithe as API
    else:
        initial = { 'url': request.GET.get('url') }
        if initial['url'] == 'referer':
            initial['url'] = request.META.get('HTTP_REFERER')
        form = ShortURLForm(initial=initial)

    ## render the form template
    template_name = template_name or 'base_shorturl_create.html'
    return render_to_response(template_name, locals(),
        context_instance=RequestContext(request))

def preview(request, code=None, api=False, template_name=None):

    ## if the page is being accessed as API, return the clean data
    if api is True:
        if code is None:
            url = request.GET.get('url')
            code = url.rstrip('/').split('/')[-1]
        object_id = SequenceMapper.to_decimal(code)
        try:
            shorturl = ShortURL.objects.get(pk=object_id).url
        except ShortURL.DoesNotExist:
            shorturl = ''
        return _api_response(shorturl, request.GET.get('type'))

    ## get the object id from code
    object_id = SequenceMapper.to_decimal(code)
    template_name = template_name or 'base_shorturl_preview.html'

    info_dict = {
        'queryset': ShortURL.objects,
        'object_id': object_id,
        'template_name': template_name,
    }

    return list_detail.object_detail(request, **info_dict)

def ranking(request, num_elements=10, template_name=None):

    ## get the list of objets ordered by their number of hits
    ordering = ['-hits', '-date']
    queryset = ShortURL.objects.order_by(*ordering)[:num_elements]
    template_name = template_name or 'base_shorturl_ranking.html'

    info_dict = { 
        'queryset': queryset,
        'template_name': template_name,
    }

    return list_detail.object_list(request, **info_dict)

def redirect(request, code):

    ## get the object id and lookup for the record
    object_id = SequenceMapper.to_decimal(code)
    shorturl = get_object_or_404(ShortURL, pk=object_id)

    ## record found, increment the hits and redirect
    shorturl.hits += 1
    shorturl.save()
    return HttpResponsePermanentRedirect(shorturl.url)
