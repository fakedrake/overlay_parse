import re

from overlays import Overlay

class BaseMatcher(object):
    """
    An interface for Matcher objects.
    """

    def offset_overlays(self, text, offset=0, **kw):
        raise NotImplementedError("Class %s has not implemented \
        offset_overlays" % type(self))

    def fit_overlays(self, text, start=None, end=None, **kw):
        raise NotImplementedError("Class %s has not implemented \
        fit_overlays" % type(self))

    def value(self, **kw):
        if hasattr(self, 'value_fn') and self.value_fn:
            return self.value_fn(**kw)

    def __repr__(self):
        return "<%s with props %s>" % (type(self).__name__, self.id)


class RegexMatcher(BaseMatcher):
    """
    Regex matching for matching.
    """

    def __init__(self, regex, props, value_fn=None):
        """
        Provide the regex to be matched.
        """

        if isinstance(regex, str):
            self.regex = re.compile(regex)
        else:
            self.regex = regex

        self.value_fn = value_fn
        self.props = props

        self.id = unicode(regex)

    def offset_overlays(self, text, offset=0, **kw):
        """
        Generate overlays after offset.
        :param text: The text to be searched.
        :param offset: Match starting that index. If none just search.
        :returns: An overlay or None
        """

        for m in self.regex.finditer(unicode(text)[offset:]):
            yield Overlay(text, (offset + m.start(), offset+m.end()),
                          props=self.props,
                          value=self.value(rxmatch=m))

    def fit_overlays(self, text, start=None, end=None, **kw):
        """
        Get an overlay thet fits the range [start, end).
        """

        _text = text[start or 0:]
        if end:
            _text = _text[:end]

        m = self.regex.match(unicode(_text))

        if m:
            yield Overlay(text, (start + m.start(), start+m.end()),
                          props=self.props,
                          value=self.value(rxmatch=m))

class OverlayMatcher(BaseMatcher):
    """
    Match a matcher. A matcher matches in 3 ways:
    - Freely with an offset
    - Fitting in a range.

    The value_fn should accept the `overlay' keyword.
    """

    def __init__(self, props_match, props=None, value_fn=None):
        """
        :param props: Set of props to be matched.
        """

        self.props_match = props_match
        self.props = props or set()

        self.id = unicode(self.props_match)

    def offset_overlays(self, text, offset=0, **kw):
        """
        Get overlays for the text.
        :param text: The text to be searched. This is an overlay
        object.
        :param offset: Match starting that index. If none just search.
        :returns: A generator for overlays.
        """

        for ovl in text.overlays:
            if ovl.match(offset=offset, props=self.props_match):
                yield ovl.copy(props=self.props,
                               value=self.value(overlay=ovl))

    def fit_overlays(self, text, start=None, end=None, **kw):
        """
        Get an overlay thet fits the range [start, end).
        """

        for ovl in text.overlays:
            if ovl.match(props=self.props_match, rng=(start, end)):
                yield ovl

class ListMatcher(BaseMatcher):
    """
    Match as a concatenated series of other matchers. It is greedy in
    the snse that it just matches everything.

    value_fn should accept the `ovls' keyword which is a list of the
    overlays that compose the result.
    """

    def __init__(self, matchers, props=None, value_fn=None, dependencies=None):
        self.matchers = matchers
        self.props = props or set()
        self.value_fn = value_fn
        self.dependencies = dependencies or []

    def _merge_ovls(self, ovls):
        """
        Merge ovls and also setup the value and props.
        """

        ret = reduce(lambda x,y: x.merge(y), ovls)
        ret.value = self.value(ovls=ovls)
        ret.set_props(self.props)
        return ret

    def _fit_overlay_lists(self, text, start, matchers, **kw):
        """
        Return a list of overlays that start at start.
        """

        if matchers:
            for o in matchers[0].fit_overlays(text, start):
                for rest in self._fit_overlay_lists(text, o.end, matchers[1:]):
                    yield [o] + rest

        else:
            yield []


    def offset_overlays(self, text, offset=0, run_deps=True, **kw):
        """
        The heavy lifting is done by fit_overlays. Override just that for
        alternatie implementation.
        """

        if run_deps and self.dependencies:
            text.overlay(self.dependencies)

        value_ovls = []
        for ovlf in self.matchers[0].offset_overlays(text,
                                                     goffset=offset,
                                                     **kw):
            for ovll in self._fit_overlay_lists(text, ovlf.end,
                                                self.matchers[1:]):
                yield self._merge_ovls([ovlf] + ovll)

    def fit_overlays(self, text, start=None, _matchers=None,
                     run_deps=True, ovls=None, **kw):
        # Each matcher will create generate a series of overlays with
        # it's fit overlay. Ignore end for now.

        if run_deps and self.dependencies:
            text.overlay(self.dependencies)

        ovls = ovls or []

        if _matchers is None:
            _matchers = self.matchers

        for ret in self._fit_overlay_lists(text, start=start,
                                           matchers=_matchers, **kw):

            yield self._merge_ovls(ret)

class MatcherMatcher(BaseMatcher):
    """
    Match the matchers.
    """

    def __init__(self, matchers, props=None, value_fn=None):
        self.matchers = matchers
        self.props = props
        self.value_fn = value_fn

        self._list_match = ListMatcher([OverlayMatcher(m.props) for m in matchers], props=self.props)
        self._overlayed_already = []

    def _maybe_run_matchers(self, text, run_matchers):
        """
        OverlayedText should be smart enough to not run twice the same
        matchers but this is an extra handle of control over that.
        """

        if run_matchers is True or \
           (run_matchers is not False and text not in self._overlayed_already):
            text.overlay(self.matchers)
            self._overlayed_already.append(text)


    def fit_overlays(self, text, run_matchers=None, **kw):
        """
        First all matchers will run and then I will try to combine
        them. Use run_matchers to force running(True) or not
        running(False) the matchers.

        See ListMatcher for arguments.
        """
        self._maybe_run_matchers(text, run_matchers)
        for i in self._list_match.fit_overlay(text, **kw):
            yield i

    def offset_overlays(self, text, run_matchers=None, **kw):
        """
        First all matchers will run and then I will try to combine
        them. Use run_matchers to force running(True) or not
        running(False) the matchers.

        See ListMatcher for arguments.
        """

        self._maybe_run_matchers(text, run_matchers)
        for i in self._list_match.offset_overlays(text, **kw):
            yield i


def mf(pred, props=None, value_fn=None, props_on_match=False):
    """
    Matcher factory.
    """

    if isinstance(pred, BaseMatcher):
        return pred if props_on_match else pred.props

    if isinstance(pred, str) or \
       type(pred).__name__ == 'SRE_Pattern':
        return RegexMatcher(pred, props=props, value_fn=value_fn)

    if isinstance(pred, set):
        return OverlayMatcher(pred, props=props, value_fn=value_fn)

    if isinstance(pred, list):
        deps = [p for p in pred if isinstance(p, BaseMatcher)]
        return ListMatcher([mf(p, props_on_match=True) for p in pred],
                           props=props, value_fn=value_fn,
                           dependencies=deps)
