"""
Regular Expression Hierarchical Parsing.
"""

from .util import Rng


class Overlay(object):

    def __init__(self, text, rng, props=None, value=None):
        """
        :param text: The text this overlay refers to.
        :param start: The starting index of the overlay.
        :param end: The end index of the overlay.
        :param props: A list of strings that are the properties of the
        overlay.
        :param value: The value that this text represents.
        """
        (start, end) = rng
        self.text = text
        self.start = start
        self.end = end
        self.value = value
        self.priority = False

        self.set_props(props)

    def __lt__(self, ovl):
        if self.priority < ovl.priority:
            return True

        return len(self) < len(ovl)

    def set_props(self, props=None):
        """
        Set props of this overlay or clear them.
        """

        self.props = props or set()

    def copy(self, props=None, value=None):
        """
        Copy the Overlay possibly overriding props.
        """

        return Overlay(self.text,
                       (self.start, self.end),
                       props=props or self.props,
                       value=value or self.value)

    def __str__(self):
        """
        The text tha this overlay matches.
        """

        return unicode(self.string())

    def __len__(self):
        return self.end - self.start

    def before(self):
        """
        The text before the overlay.
        """

        return self.text[:self.start]

    def after(self):
        """
        The entire text after the overlay.
        """

        return self.text[self.end:]

    def until(self, ovl):
        """
        The text separating overlays.
        """

        return self.text[self.end:ovl.start]

    def string(self):
        return self.text[self.start:self.end]

    def merge(self, ovl):
        if not ovl:
            return self

        if self.text != ovl.text:
            raise ValueError("Overlays refer to different texts.")

        s = min(self.start, ovl.start)
        e = max(self.end, ovl.end)

        return Overlay(self.text, (s, e), self.props.union(ovl.props))

    def __eq__(self, ov):
        return self.start == ov.start and \
            self.end == ov.end and \
            unicode(self.text) == unicode(ov.text)

    def __repr__(self):
        return u"<Overlay object at [%d, %d), props: %s, text: '%s'>" % (
            self.start, self.end, self.props, unicode(self))

    def match(self, props=None, rng=None, offset=None):
        """
        Provide any of the args and match or dont.

        :param props: Should be a subset of my props.
        :param rng: Exactly match my range.
        :param offset: I start after this offset.
        :returns: True if all the provided predicates match or are None
        """

        if rng:
            s, e = rng
        else:
            e = s = None

        return ((e is None or self.end == e) and
                (s is None or self.start == s)) and \
            (props is None or props.issubset(self.props)) and \
            (offset is None or self.start >= offset)


class OverlayedText(object):

    """
    Both the text and it's overlays.
    """

    def __init__(self, text, overlays=None):
        self.text = text
        self.overlays = overlays or []
        self._ran_matchers = []

    def copy(self):
        t = OverlayedText(self.text, [o.copy() for o in self.overlays])
        t._ran_matchers = [i for i in self._ran_matchers]
        return t

    def __unicode__(self):
        try:
            return unicode(self.text)
        except UnicodeDecodeError:
            ascii_text = str(self.text).encode('string_escape')
            return unicode(ascii_text)

    def __str__(self):
        try:
            return str(self.text)
        except UnicodeEncodeError:
            ascii_text = unicode(self.text).encode('unicode_escape')
            return ascii_text

    def __repr__(self):
        return unicode(self.text)

    def __getitem__(self, key):
        return OverlayedText(self.text.__getitem__(key),
                             overlays=self.overlays_at(key))

    def overlays_at(self, key):
        """
        Key may be a slice or a point.
        """

        if isinstance(key, slice):
            s, e, _ = key.indices(len(self.text))
        else:
            s = e = key

        return [o for o in self.overlays if o.start in Rng(s, e)]

    def overlay(self, matchers, force=False):
        """
        Given a list of matchers create overlays based on them. Normally I
        will remember what overlays were run this way and will avoid
        re-running them but you can `force` me to. This is the
        recommended way of running overlays.c
        """

        for m in matchers:
            if m in self._ran_matchers:
                continue

            self._ran_matchers.append(m)
            self.overlays += list(m.offset_overlays(self))

        self.overlays.sort(key=lambda o: o.start, reverse=True)

    def get_overlays(self, **kw):
        """
        See Overlay.match() for arguments.
        """

        return [o for o in self.overlays if o.match(**kw)]
