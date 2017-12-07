# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
from django.test import TestCase

# Create your tests here.
from transmissionrpc import Torrent

from txmgr.views import TorrentView


class TorrentMediaTypeTestCase(TestCase):
    def test_episode(self):
        t = TorrentView(Torrent(None, dict(id=1, name='Some.Show.S07E13.720p.HDTV.x264-AVS')))
        assert t.name == 'Some.Show.S07E13.720p.HDTV.x264-AVS'
        assert t.media_type() == 'episode'

    def test_movie(self):
        t = TorrentView(Torrent(None, dict(id=1, name='Fantastic.Film.2016.720p.BluRay.x264-DRONES')))
        assert t.media_type() == 'movie'

    def test_season(self):
        t = TorrentView(Torrent(None, dict(id=1, name='Germanium.Mountain.S01.720p.HDTV.DD5.1.x264-CtrlHD')))
        assert t.media_type() == 'season'

    def test_many(self):
        types = {
            'Some.Show.S07E13.720p.HDTV.x264-AVS': 'episode',
            'Fantastic.Film.2016.720p.BluRay.x264-DRONES': 'movie',
            'Germanium.Mountain.S01.720p.HDTV.DD5.1.x264-CtrlHD': 'season',
            'Modern Family S07E21 Crazy Train 720p WEB-DL DD5.1 H.264-Oosh.mkv': 'episode',
            'Marvels.Agents.of.S.H.I.E.L.D.S04E05.720p.HEVC.x265-MeGusta': 'episode',
            'The Big Bang Theory S09E24 The Convergence Convergence 720p WEB-DL DD5.1 H.264-Oosh.mkv': 'episode',
            'The.X-Files.COMPLETE.720p.WEBRip.H.264-TD': 'movie',
        }

        failed = 0

        for name, mt in types.items():
            t = TorrentView(Torrent(None, dict(id=1, name=name)))
            if not t.media_type() == mt:
                failed += 1
                sys.stderr.write("{} listed as {} but {}\n".format(name, mt, t.media_type()))

        assert failed == 0, "{} checks failed".format(failed)
