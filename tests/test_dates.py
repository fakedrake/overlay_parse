#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_dates
----------------------------------

Tests for `dates` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from overlay_parse.dates import just_dates, just_ranges

class TestDates(unittest.TestCase):

    def setUp(self):
        pass

    def test_simple_dates(self):
        dates = just_dates("Timestamp: 22071991: She said she was \
        coming on april the 18th, it's 26 apr 2014 and hope is leaving me.")

        self.assertIn((22, 7, 1991), dates)
        self.assertIn((18, 4, 0), dates)
        self.assertIn((26, 4, 2014), dates)

    def test_range(self):
        rng = just_ranges("I will be there from 2008 to 2009")

        self.assertEqual(rng, "")

    def test_present(self):
        pass

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
