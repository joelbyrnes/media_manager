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

    def media_name(self):
        if self.media_type() == 'episode':
            tvmatch = re.match("(.*)[ .][sS]([0-9]{1,2})[eE]([0-9]{1,2})", self.name)
            show = tvmatch.group(1).replace('.', ' ')

            print("looks like TV show: " + show)
            print("season " + tvmatch.group(2))
            print("episode " + tvmatch.group(3))
            return show

        elif self.media_type() == 'season':
            seasonmatch = re.match("(.*)[ .][sS]([0-9]{1,2})", self.name)
            show = seasonmatch.group(1).replace('.', ' ')

            print("looks like season pack of TV show: " + show)
            print("season " + seasonmatch.group(2))
            return show

        elif self.media_type() == "movie":
            moviematch = re.match("(.*)([1-2]{1}[0-9]{3})[ .]", self.name)
            if moviematch:
                movie = moviematch.group(1).replace('.', ' ').strip()

                print("looks like movie: {}".format(movie))
                print("year: {}".format(moviematch.group(2)))
                return movie

            else:   # probably no year
                moviematch = re.match("(.*)[ .]", self.name)
                movie = moviematch.group(1).replace('.', ' ').strip()
                print("looks like movie: {}".format(movie))
                return movie


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
