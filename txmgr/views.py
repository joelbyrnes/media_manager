# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

import transmissionrpc
from django.conf import settings
from django.views import generic

logger = logging.getLogger(__name__)


class IndexView(generic.ListView):
    template_name = 'txmgr/index.html'
    context_object_name = 'torrents'

    def get_queryset(self):
        logger.debug("Connect to Transmission")
        tc = transmissionrpc.Client(**settings.TRANSMISSION_CONFIG)
        logger.debug("get_torrents")
        torrents = tc.get_torrents()
        logger.debug("got torrents")

        return sorted(torrents, key=lambda x: x.name)
