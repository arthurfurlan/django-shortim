# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse
from models import ShortURL
from datetime import datetime
import subprocess
import os

DEFAULT_SITE_DOMAIN = 'example.com'

def change_site_domain(sender, **kwargs):

    if not kwargs.get('interactive'):
        return

    ## check if the domain was not configured yet
    current_site = sender.Site.objects.get_current()
    if current_site.domain != DEFAULT_SITE_DOMAIN:
        return

    ## check if the user wants to configure the site
    print '\nThe current site domain is "%s".' % current_site.domain
    prompt = 'Would you like to change it now? (yes/no): '
    option = ''
    while option.lower() != 'yes':
        option = raw_input(prompt)
        if option.lower() == 'no':
            return

    ## get the new site domain
    answer = ''
    prompt = 'Site domain: '
    while not answer:
        answer = raw_input(prompt)
    current_site.domain = answer

    ## get the new site name
    prompt = 'Site name: [%s] ' % current_site.domain
    answer = raw_input(prompt)
    current_site.name = answer or current_site.domain

    current_site.save()
    print 'Current site configured.\n'

def create_first_shorturl(sender, **kwargs):

    if not kwargs.get('interactive'):
        return

    ## check if the database contains some URL
    if ShortURL.objects.count() > 0:
        return

    ## check if the user wants to configure the site
    prompt = 'Would you like to create a first short URL pointing to this site? (yes/no): '
    option = ''
    while option.lower() != 'yes':
        option = raw_input(prompt)
        if option.lower() == 'no':
            return

    ## create the first url
    current_site = sender.Site.objects.get_current()
    scheme = getattr(settings, 'SHORTIM_SITE_SCHEME', 'http')
    url = scheme.lower() + '://' + current_site.domain \
            + reverse('shortim_create')

    shorturl = ShortURL(url=url, remote_user='127.0.0.1')
    shorturl.save()
    print 'First short URL created: %s\n' % shorturl.get_absolute_full_url()

def upload_301works(*args, **kwargs):

    ## create the 301works.org file
    unique_identifier = settings.SHORTIM_301WORKS_CREATOR \
        + '.' + datetime.now().strftime('%Y.%m.%d')
    temp_file = '/tmp/%s.csv' % unique_identifier
    f = open(temp_file, 'w+')
    for u in ShortURL.objects.all().order_by('id'):
        line = u'%s,%s,%s,%d\n' % (u.get_short_full_url(),
                u.url, u.date.isoformat(), u.hits)
        f.write(line.encode('utf-8'))
    f.close()

    ## create the upload command via curl (FIXME: rewrite using pycurl)
    curl_command = "curl -v --location --header 'x-amz-auto-make-bucket:1' " \
        + "--header 'x-archive-meta01-collection:%s' " \
        + "--header 'x-archive-meta-mediatype:software' " \
        + "--header 'x-archive-meta-title:%s' " \
        + "--header 'x-archive-meta-description:A list of all urls in the %s database as of %s' " \
        + "--header 'x-archive-meta-creator:%s' " \
        + "--header 'authorization: LOW %s:%s' " \
        + "--upload-file %s " \
        + "http://s3.us.archive.org/%s/%s"
    curl_command = curl_command % (
            settings.SHORTIM_301WORKS_COLLECTION,
            unique_identifier,
            settings.SHORTIM_301WORKS_CREATOR,
            datetime.now().strftime('%Y-%m-%d'),
            settings.SHORTIM_301WORKS_CREATOR,
            settings.SHORTIM_301WORKS_ACCESSKEY,
            settings.SHORTIM_301WORKS_SECRETKEY,
            temp_file,
            unique_identifier,
            os.path.basename(temp_file),
    )

    ## execute the command and upload the file
    subprocess.call(curl_command, shell=True)
    os.unlink(temp_file)
