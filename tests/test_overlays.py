#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_overlays
----------------------------------

Tests for `overlays` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from overlay_parse.overlays import OverlayedText
from overlay_parse.matchers import mf, MatcherMatcher


class TestOverlay(unittest.TestCase):

    def setUp(self):
        self.text = OverlayedText("Hello World")

        # Matchers
        self.o = mf("o",
               {'hello','2'})
        self.hell = mf("[hH]ell",
                  {'hello','1'})
        self.space = mf(" ",
                   {'space'})
        hello = mf([{'hello','1'}, {'hello','2'}, {'space'}],
                   {'hello', 'full'})

        # Create overlays from matchers
        self.text.overlay([self.hell, self.o, self.space, hello])

    def test_hello(self):
        self.assertEqual(unicode(self.text.get_overlays(props={'full'})[0]), "Hello ")

    def test_mathcer_matcher(self):
        t2 = self.text.copy()
        hello_cool = MatcherMatcher([self.hell, self.o, self.space], {"hello", "smart"})
        t2.overlay([hello_cool])

        self.assertEqual(unicode(t2.get_overlays(props={'full'})[0]), "Hello ")

    def test_unicode_text(self):
        t = OverlayedText('28 July 1914\xc2\xa0\xe2\x80\x93 11')
        self.assertEqual(str(t), '28 July 1914\xc2\xa0\xe2\x80\x93 11')

    def test_unicode_matcher(self):
        m =  mf("rx", {})
        self.assertEqual(list(m.offset_overlays(u"\xc2\xa0\xe2\x80\x93")), [])


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
