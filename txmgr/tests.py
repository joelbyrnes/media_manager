# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
from django.test import TestCase

# Create your tests here.
from transmissionrpc import Torrent

from txmgr.views import TorrentView


class TorrentMediaTestCase(TestCase):
    def test_episode(self):
        t = TorrentView(Torrent(None, dict(id=1, name='Some.Show.S07E13.720p.HDTV.x264-AVS')))
        assert t.name == 'Some.Show.S07E13.720p.HDTV.x264-AVS'
        assert t.media_type() == 'episode'
        assert t.media_title() == 'Some Show'

    def test_movie(self):
        t = TorrentView(Torrent(None, dict(id=1, name='Fantastic.Film.2016.720p.BluRay.x264-DRONES')))
        assert t.media_type() == 'movie'
        assert t.media_title() == 'Fantastic Film', t.media_name()

    def test_season(self):
        t = TorrentView(Torrent(None, dict(id=1, name='Germanium.Mountain.S01.720p.HDTV.DD5.1.x264-CtrlHD')))
        assert t.media_type() == 'season'
        assert t.media_title() == 'Germanium Mountain'

    def test_many(self):
        types = {
            'Some.Show.S07E13.720p.HDTV.x264-AVS': ('episode', 'Some Show'),
            'Fantastic.Film.2016.720p.BluRay.x264-DRONES': ('movie', 'Fantastic Film'),
            'It\'s.Complicated.2009.WS.DVDRip.x264.AC3-REKoDE': ('movie', 'It\'s Complicated'),
            'Germanium.Mountain.S01.720p.HDTV.DD5.1.x264-CtrlHD': ('season', 'Germanium Mountain'),
            'Modern Family S07E21 Crazy Train 720p WEB-DL DD5.1 H.264-Oosh.mkv': ('episode', 'Modern Family'),
            'Marvels.Agents.of.S.H.I.E.L.D.S04E05.720p.HEVC.x265-MeGusta':
                ('episode', 'Marvels Agents of S H I E L D'),
            'The Big Bang Theory S09E24 The Convergence Convergence 720p WEB-DL DD5.1 H.264-Oosh.mkv':
                ('episode', 'The Big Bang Theory'),
            'The.X-Files.COMPLETE.720p.WEBRip.H.264-TD': ('multi-season', 'The X-Files'),
            'The.Wire.S01-S05.720p.BluRay.nHD.x264-NhaNc3': ('multi-season', 'The Wire'),
        }

        failed = 0

        for name, (mt, mn) in types.items():
            t = TorrentView(Torrent(None, dict(id=1, name=name)))
            if not t.media_type() == mt:
                failed += 1
                sys.stderr.write("{} type should be {} but was {}\n".format(name, mt, t.media_type()))
            if not t.media_title() == mn:
                failed += 1
                sys.stderr.write("{} name should be {} but was {}\n".format(name, mn, t.media_title()))

        assert failed == 0, "{} checks failed".format(failed)
