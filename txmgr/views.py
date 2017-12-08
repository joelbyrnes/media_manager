# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import re

import transmissionrpc
from datetime import datetime

import PTN
from django.conf import settings
from django.views import generic
from plexapi.exceptions import NotFound
from plexapi.server import PlexServer

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
        elif self.media_info.get('seasons'):
            return 'seasons'

        return 'movie'

    def media_title(self):
        return self.media_info.get('title')

    @staticmethod
    def parse_media_info(name):
        parsed = PTN.parse(name)

        if parsed.get('episode'):
            return parsed

        # additional processing required

        seasonsmatch = re.search("(.*)[ .]([sS][0-9]{1,2}-[sS][0-9]{1,2}|COMPLETE)", name)

        if seasonsmatch:
            parsed['title'] = seasonsmatch.group(1).replace('.', ' ')
            parsed['seasons'] = seasonsmatch.group(2)
            return parsed

        seasonmatch = re.search("(.*)[ .][sS]([0-9]{1,2})", name)

        if seasonmatch:
            parsed['title'] = seasonmatch.group(1).replace('.', ' ')
            parsed['season'] = seasonmatch.group(2)
            return parsed

        if parsed.get('year'):
            # more likely a movie if not an episode
            moviematch = re.match("(.*)([1-2]{1}[0-9]{3})[ .]", name)
            if moviematch:
                parsed['title'] = moviematch.group(1).replace('.', ' ').strip()

        return parsed


def find_plex_media_for_torrent(plex, tv):
    result = None
    try:
        if tv.media_type() == 'movie':
            result = plex.library.section('Downloaded Movies').get(tv.media_title())
        elif tv.media_type() == 'season' or tv.media_type() == 'seasons':
            result = plex.library.section('Downloaded TV').get(tv.media_title())
        elif tv.media_type() == 'episode':
            show = plex.library.section('Downloaded TV').get(tv.media_title())
            season = show.season(tv.media_info['season'])
            result = next(filter(lambda e: e.index == tv.media_info['episode'], season.episodes()), None)

    except NotFound as e:
        pass

    if not result:
        logger.debug("Can't find {} in Plex".format(tv.media_title()))

    return result


class IndexView(generic.ListView):
    template_name = 'txmgr/index.html'
    context_object_name = 'torrents'

    def get_queryset(self):
        logger.debug("Connect to Transmission")
        tc = transmissionrpc.Client(**settings.TRANSMISSION_CONFIG)

        logger.debug("Connect to Plex")
        baseurl = 'http://192.168.0.10:32400'
        token = 'abcd'
        plex = PlexServer(baseurl, token)

        torrents = []
        logger.debug("get_torrents")
        for t in tc.get_torrents()[0:30]:
            tv = TorrentView(t)
            tv.plexinfo = find_plex_media_for_torrent(plex, tv)
            torrents.append(tv)
        logger.debug("got torrents")

        return sorted(torrents, key=lambda x: x.name)
