# -*- coding: utf-8 -*-

from datetime import date

import re
import itertools

from overlays import OverlayedText, Rng
from matchers import mf
from util import *

def month_names(rxmatch):
    for i,m in enumerate(MONTH_NAMES_LONG):
        if starts_with(m, rxmatch.group(0)):
            return i+1

def date_range(ovls):
    d2 = ovls[2].value
    d1 = ovls[0].value

    if d2[2] < 0 and d1[2] > 0:
        d, m, y = d1
        return ((d, m, -y), d2)

    for i1,i2 in reversed(zip(d1, d2)):
        if i1 > i2:
            return (d2, d1)

        if i2 > i1:
            return (d1, d2)

    return (d1, d2)

def present(rxmatch):
    d = date.today()
    return (d.day, d.month, d.year)

def date_tuple(ovls):
    """
    We should have a list of overlays from which to extract day month
    year.
    """

    day = month = year = 0
    for o in ovls:
        if 'day' in o.props:
            day = o.value

        if 'month' in o.props:
            month = o.value

        if 'year' in o.props:
            year = o.value

        if 'date' in o.props:
            day, month, year = [(o or n) for o, n in zip((day, month,
                                                          year), o.value)]

    return (day, month, year)

def longest_overlap(ovls):
    """
    From a list of overlays if any overlap keep the longest.
    """

    # Ovls know how to compare to each other.
    ovls = sorted(ovls)

    # I know this could be better but ovls wont be more than 50 or so.
    for i, s in enumerate(ovls):
        passing = True

        for l in ovls[i+1:]:
            if s.start in Rng(l.start, l.end, rng=(True, True)) or \
               s.end in Rng(l.start, l.end, rng=(True, True)):
                passing = False
                break

        if passing:
            yield s

MONTH_NAMES_LONG = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

MONTH_NAMES_SHORT = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

matchers = [
    # Regex
    ('day', mf(r"(0[1-9]|[12][0-9]|3[01]|[1-9])",
               {'day', 'num'}, rx_int)),
    ('day', mf(w(r"(0[1-9]|[12][0-9]|3[01]|[1-9])"),
               {'day', 'num', 'word'}, rx_int)),

    ('day_numeric', mf(w(r"(11th|12th|13th|[012][4-9]th|[4-9]th|[123]0th|[0-3]1st|[02]2nd|023rd)"),
                       {'day', 'numeric'}, rx_int_extra)),

    # Note that regexes are greedy. If there is '07' then '7' alone
    # will be ignored
    ('month', mf(r"(0[1-9]|1[012]|[1-9])", {'month', 'num'}, rx_int)),

    ('year_4', mf(r"\d{4}", {'year', '4dig', 'num'}, rx_int)),

    ('year_num', mf(w(r"\d+\s*([Aa]\.?[Dd]\.?)"), {'year', 'adbc', 'num', "ad", 'word'},
                    rx_int_extra)),

    ('year_adbc', mf(w(r"\d+\s*([Bb]\.?[Cc]\.?([Ee]\.?)?)"), {"year", "adbc", "bc", 'word'},
                     lambda rxmatch: -rx_int_extra(rxmatch))),

    ('year_num_word', mf(w(r"\d{1,4}"), {'year', 'num', 'word'},
                         rx_int)),


    ('month_name_short', mf(re.compile(r"(%s)" % "|".join(words(MONTH_NAMES_SHORT)), re.I),
                            {"month", "name", "short"}, month_names)),

    ('month_name_long', mf(re.compile(r"(%s)" % "|".join(words(MONTH_NAMES_LONG)), re.I),
                           {"month", "name", "long"}, month_names)),

    # Note that instead of rx or sets you can use a matcher, it will
    # be a dependency

    # Lists

    # June 1991
    ("far_year", mf([{"month", "name"}, r"\s+", {"year", '4dig'}],
                    {"date", "year_month"},
                    date_tuple)),

    # July the 14th
    ('dayn_month_date', mf([{'month', 'name'},
                            r",?\s*(the)?\s+",
                            {'day', 'numeric'}],
                           {"day_month", "numeric", "date"}, date_tuple)),

    # July 14
    ('dayn_month_date', mf([{'month', 'name'}, r"\s+", {'day', 'word'}],
                           {"day_month", "date"}, date_tuple)),


    # July the 14th 1991
    ('dayn_month_year_date', mf([{'day_month'}, ur"(\s+|\s*,\s*)",
                                 {"year", "word"}],
                                {"day_month_year", "numeric", "date", "full"},
                                date_tuple)),

    # 14 July 1991
    ('day_month_year_full', mf([{"day"}, r"\s+(of\s+)?",
                                {"month", "name"}, r"\s+",
                                {"year", "word"}],
                               { "day_month_year", "date"},
                               date_tuple)),

    # 3000AD
    ("far_year", mf([{"year", 'word'}],
                    {"date", "only_year"},
                    date_tuple)),

    # July 13, 1991
    ('month_day_year', mf([{'day_month'}, ur"(\s+|\s*,?\s*)", "year"],
                          {"month_day_year", "date"},
                          date_tuple)),


    # Present
    ('present', mf(r"([pP]resent|[Tt]oday|[Nn]ow)", {"date", "present"}, present)),
]

# Short dates
SEPARATORS = [r"/", r"\.", r"\|", r"-"]


matchers += [('ymd_dates_%s' % s,
              mf([{'year', 'num', 'word'}, s, {'month', 'num'}, s, {'day', 'num'}],
                 {"date", 'short', 'ymd', "sep_%s"%s}, date_tuple))
             for s in SEPARATORS]

matchers += [('dmy_dates_%s' % s,
              mf([{'day', 'num'}, s, {'month', 'num'}, s, {'year', 'num', 'word'}],
                 {"date", 'short', 'dmy', "sep_%s"%s}, date_tuple))
             for s in SEPARATORS]

matchers += [("mdy_dates_%s" % s,
              mf([{'month', 'num'}, s, {'day', 'num'}, s, {'year', 'num', 'word'}],
                 {"date", 'short', 'mdy', "sep_%s"%s}, date_tuple))
             for s in SEPARATORS]


# Non separated

matchers += [('ymd_dates',
              mf([{'year', 'num'}, {'month', 'num'}, {'day', 'num'}],
                 {"date", 'short', 'ymd', "nosep"}, date_tuple)),
             ('dmy_dates',
              mf([{'day', 'num'}, {'month', 'num'}, {'year', 'num'}],
                 {"date", 'short', 'dmy', "nosep"}, date_tuple)),
             ("mdy_dates",
              mf([{'month', 'num'}, {'day', 'num'}, {'year', 'num'}],
                 {"date", 'short', 'mdy', "sep_%s"}, date_tuple)),]

matchers += [
    # Date range
    ("range", mf([{"date"},
                  ur"\s*(-|\sto\s|\suntil\s|\xe2\x80\x93|\u2013)\s*",
                  {"date"}],
                 {"range"}, date_range)),

    # # November 20, 1876 in Shusha, Russian Empire – February 1, 1944 in Yerevan
    # ("range", mf([{"date"},
    #               ur"\s*(-|\sto\s|\suntil\s|\xe2\x80\x93|\u2013)\s*",
    #               {"date"}],
    #              {"range"}, date_range)),

]



def just_props(text, *props_lst, **kw):
    t = OverlayedText(text)
    t.overlay([m for n, m in matchers])
    ovls = itertools.chain(*[t.get_overlays(props=props) for props in
                             props_lst])

    values = kw.get('values', True)
    return [i.value if values else i
            for i in sorted(longest_overlap(ovls),
                            key=lambda o: o.start)]

def just_dates(text):
    return just_props(text, {'date'})


def just_ranges(text):
    return just_props(text, {'range'})


if __name__ == "__main__":
    from pprint import pprint

    pprint(just_dates("Timestamp: 22071991, well\
    i said i was on July 22 1992 but I lied."))
