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

from overlay_parse.dates import just_dates, just_ranges, just_props

class TestDates(unittest.TestCase):

    def setUp(self):
        pass

    def test_merkam(self):
        rngs = just_ranges(u"October 1872 – 2 February 1959")
        self.assertEqual(rngs, [((0, 10, 1872), (2, 2, 1959))])

    def test_simple_dates(self):
        dates = just_dates("Timestamp: 22071991: She said she was \
        coming on april the 18th, it's 26 apr 2014 and hope is leaving me.")

        self.assertIn((22, 7, 1991), dates)
        self.assertIn((18, 4, 0), dates)
        self.assertIn((26, 4, 2014), dates)

    def test_bc(self):
        dates = just_dates("200 AD 300 b.c.")

        self.assertIn((0,0,-300), dates)

    def test_range(self):
        rng = just_ranges(u"I will be there from 2008 to 2009")
        self.assertEqual(rng, [((0, 0, 2008), (0, 0, 2009))])

        rng = just_ranges(u"c. 2001–2002")
        self.assertEqual(rng, [((0, 0, 2001), (0, 0, 2002))])

    def test_range_incoherent(self):
         rng = just_ranges("I will be here from 30th of september 2006 to 18.7.2007")
         self.assertEqual(rng, [((30, 9, 2006), (18, 7, 2007))])

    def test_present(self):
        rng = just_ranges("I will stay from July the 20th until today")

        self.assertEqual(rng[0][0], (20, 7, 0))

    def test_range_partadbc(self):
        rng = just_ranges("Jesus was born somewhere in 7-4 BC")
        self.assertEqual(rng, [((0, 0, -7), (0, 0, -4))])

    def test_combo(self):
        rng = just_props("Jesus was born somewhere in 7-4 BC and also there are people who just say 8BC", {'date'}, {'range'})
        self.assertEqual(rng[0], ((0, 0, -7), (0, 0, -4)))

    def test_jamies_bday(self):

        dates = just_dates('{{Birth date and age|1969|7|10|df=y}}')
        self.assertEqual(dates, [(10,7,1969)])

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
