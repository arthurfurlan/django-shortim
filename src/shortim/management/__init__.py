# -*- coding: utf-8 -*-

from django.db.models.signals import post_syncdb
from django.contrib.sites import models as sites_models
from signals import change_site_domain, create_first_shorturl
import models as shortim_models

post_syncdb.connect(change_site_domain, sender=sites_models)
post_syncdb.connect(create_first_shorturl, sender=shortim_models)
