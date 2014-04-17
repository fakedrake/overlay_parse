import re
from datetime import date

from overlays import OverlayedText, Rng
from matchers import mf
from util import *

def month_names(rxmatch):
    for i,m in enumerate(MONTH_NAMES_LONG):
        if starts_with(m, rxmatch.group(0)):
            return i+1

def date_range(ovls):
    d1 = ovls[0].value
    d2 = ovls[2].value

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

    ovls = sorted(ovls, key=lambda x: x.end-x.start)

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
    ('day', mf(r"([012]?[1-9]|3[01])", {'day', 'num'}, rx_int)),

    ('day_numeric', mf(w(r"(11th|12th|13th|[012]?[4-9]th|[123]0th|[0-3]1st|[02]2nd|023rd)"),
                       {'day', 'numeric'}, rx_int_extra)),

    # Note that regexes are greedy. If there is '07' then '7' alone
    # will be ignored
    ('month', mf(r"(0?[1-9]|1[012])", {'month', 'num'}, rx_int)),

    ('year_4', mf(r"\d{4}", {'year', '4dig', 'num', "ad"}, rx_int)),

    ('year_num', mf(r"\d+\s*([Aa]\.?[Dd]\.?)?", {'year', 'adbc', 'num', "ad"},
                    rx_int_extra)),

    ('year_adbc', mf(w(r"\d+\s*([Bb]\.?[Cc]\.?)"), {"year", "adbc", "bc"},
                     lambda rxmatch: -rx_int_extra(rxmatch))),

    ('month_name_short', mf(re.compile(r"(%s)" % "|".join(words(MONTH_NAMES_SHORT)), re.I),
                            {"month", "name", "short"}, month_names)),

    ('month_name_long', mf(re.compile(r"(%s)" % "|".join(words(MONTH_NAMES_LONG)), re.I),
                           {"month", "name", "long"}, month_names)),

    # Note that instead of rx or sets you can use a matcher, it will
    # be a dependency

    # Lists
    # July the 14th
    ('dayn_month_date', mf([{'month', 'name'}, r",?\s*(the)?\s+", {'day', 'numeric'}],
                           {"day_month", "numeric", "date"}, date_tuple)),

    # July the 14th 1991
    ('dayn_month_year_date', mf([{'numeric', 'day_month'}, r"\s+", {"year"}],
                                {"day_month_year", "numeric", "date", "full"},
                                date_tuple)),

    # 14 July 1991
    ('day_month_year_full', mf([{"day"}, r"\s+(of\s+)?", {"month", "name"}, r"\s+", {"year"}],
                               { "day_month_year", "date"},
                               date_tuple)),

    # June 1991
    ("far_year", mf([{"month", "name"}, r"\s+", {"year"}],
                    {"date", "year_month"},
                    date_tuple)),

    # 3000AD
    ("far_year", mf([{"year"}],
                    {"date", "only_year"},
                    date_tuple)),

    # Present
    ('present', mf(r"([pP]resent|[Tt]oday|[Nn]ow)", {"date", "present"}, present)),
]

# Short dates
SEPARATORS = [r"", r"/", r"\.", r"\|", r"-"]

matchers += [('dmy_dates_%s' % s,
              mf([{'day', 'num'}, s, {'month', 'num'}, s, {'year', 'num'}],
                 {"date", 'short', 'dmy', "sep_%s"%s}, date_tuple))
             for s in SEPARATORS]

matchers += [("mdy_dates_%s" % s,
              mf([{'month', 'num'}, s, {'day', 'num'}, s, {'year', 'num'}],
                 {"date", 'short', 'mdy', "sep_%s"%s}, date_tuple))
             for s in SEPARATORS]

matchers += [('ymd_dates_%s' % s,
              mf([{'year', 'num'}, s, {'month', 'num'}, s, {'day', 'num'}],
                 {"date", 'short', 'ymd', "sep_%s"%s}, date_tuple))
             for s in SEPARATORS]

matchers += [
    # Date range
    ("range", mf([{"date"}, r"\s*(-|\sto\s|\suntil\s)\s*", {"date"}],
                 {"range"}, date_range)),
]


def just_dates(text):
    t = OverlayedText(text)
    t.overlay([m for n,m in matchers])

    return [i.value for i in
            longest_overlap(t.get_overlays(props={'date'}))]

def just_ranges(text):
    t = OverlayedText(text)
    t.overlay([m for n,m in matchers])

    return [i.value for i in
            longest_overlap(t.get_overlays(props={'range'}))]


if __name__ == "__main__":
    from pprint import pprint

    pprint(just_dates("Timestamp: 22071991, well\
    i said i was on July 22 1992 but I lied."))
