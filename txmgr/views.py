# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import re

import transmissionrpc
from datetime import datetime

import PTN
from django.conf import settings
from django.views import generic

logger = logging.getLogger(__name__)


def list_has_rars(files):
    for f in files:
        if f.lower().endswith(".rar") or f.lower().endswith(".r00"):
            logger.debug("found rar-like file %s" % f)
            return True
    return False


class TorrentView(object):
    def __init__(self, torrent):
        self.torrent = torrent
        self.media_info = self.parse_media_info(torrent.name)

    def __getattr__(self, key):
        return getattr(self.torrent, key)

    # def __setattr__(self, key, value):
    #     return setattr(self.torrent, key, value)

    def has_rars(self):
        return list_has_rars([f['name'] for f in self.torrent.files().values()])

    def percent_done_string(self):
        return "{:.1%}".format(self.torrent.percentDone)

    def done_date(self):
        return datetime.fromtimestamp(self.torrent.doneDate)

    def media_type(self):
        if self.media_info.get('episode'):
            return 'episode'
        elif self.media_info.get('season'):
            return 'season'

        seasonmatch = re.search("(.*)[ .][sS]([0-9]{1,2})", self.name)

        if seasonmatch:
            return "season"

        # todo multi-season
        # eg Mission.Impossible.1966.S01-S04.Complete.DVDRip.XviD-TD
        # eg The.Wire.S01-S05.720p.BluRay.nHD.x264-NhaNc3

        return 'movie'

    def media_title(self):
        return self.media_info.get('title')

    @staticmethod
    def parse_media_info(name):
        parsed = PTN.parse(name)

        if parsed.get('episode'):
            return parsed

            # additional processing required

        seasonmatch = re.search("(.*)[ .][sS]([0-9]{1,2})", name)

        if seasonmatch:
            parsed['title'] = seasonmatch.group(1).replace('.', ' ')

            print("looks like season pack of TV show: " + parsed['title'])
            print("season " + seasonmatch.group(2))

            parsed['season'] = seasonmatch.group(2)

        return parsed


class IndexView(generic.ListView):
    template_name = 'txmgr/index.html'
    context_object_name = 'torrents'

    def get_queryset(self):
        logger.debug("Connect to Transmission")
        tc = transmissionrpc.Client(**settings.TRANSMISSION_CONFIG)
        logger.debug("get_torrents")
        torrents = map(TorrentView, tc.get_torrents())
        logger.debug("got torrents")

        return sorted(torrents, key=lambda x: x.name)
