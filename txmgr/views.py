# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import re

import transmissionrpc
from datetime import datetime
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
        # default
        type = "movie"

        # tvmatch = "name.match /(.*)\.[sS]([0-9]{1,2})[eE]([0-9]{1,2})/"
        tvmatch = re.search("(.*)[ .][sS]([0-9]{1,2})[eE]([0-9]{1,2})", self.name)
        # seasonmatch = "name.match /(.*)\.[sS]([0-9]{1,2})/"
        seasonmatch = re.search("(.*)[ .][sS]([0-9]{1,2})", self.name)

        if tvmatch:
            type = "episode"
        elif seasonmatch:
            type = "season"

        # todo multi-season
        # eg Mission.Impossible.1966.S01-S04.Complete.DVDRip.XviD-TD
        # eg The.Wire.S01-S05.720p.BluRay.nHD.x264-NhaNc3

        return type

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
