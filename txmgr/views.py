# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

import transmissionrpc
from django.conf import settings
from django.shortcuts import render

logger = logging.getLogger(__name__)


def index(request):
    logger.debug("Connect to Transmission")
    tc = transmissionrpc.Client(**settings.TRANSMISSION_CONFIG)
    logger.debug("get_torrents")
    torrents = tc.get_torrents()
    logger.debug("got torrents")

    torrents = sorted(torrents, key=lambda x: x.name)

    return render(request, 'txmgr/index.html', {'torrents': torrents})
