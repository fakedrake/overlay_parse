import re

class Rng(object):
    """
    Open-closed range of numbers that supports `in'
    """

    def __init__(self, s, e, rng=(True, False)):
        self.s = s
        self.e = e
        self.sclosed, self.eclosed = rng

    def __contains__(self, num):
        return ((not self.eclosed and num < self.e) or \
                (self.eclosed and num <= self.e)) and \
            ((self.sclosed and num >= self.s) or \
             (not self.sclosed and num < self.s))

def w(s):
    """
    Most of the time we just want words.
    """

    return r"\b%s\b" % s

def words(l):
    return [w(i) for i in l]

def starts_with(txt, pre):
    return txt[:len(pre)].lower() == pre.lower()

def rx_int(rxmatch):
    return int(rxmatch.group(0))

def rx_int_extra(rxmatch):
    """
    We didn't just match an int but the int is what we need.
    """

    rxmatch = re.search("\d+", rxmatch.group(0))
    return int(rxmatch.group(0))
