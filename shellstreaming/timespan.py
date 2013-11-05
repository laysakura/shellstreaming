# -*- coding: utf-8 -*-
"""
    shellstreaming.timespan
    ~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides timespan [t0, t1]
"""
from shellstreaming.timestamp import Timestamp


class Timespan(object):
    """Provides timespan [start, start + span_ms]"""
    def __init__(self, start, span_ms):
        """Constructor

        :param start:   beginning of timespan
        :type start:    instance of `Timestamp <#shellstreaming.timestamp.Timestamp>`_
        :param span_ms: timespan
        """
        assert(isinstance(start, Timestamp))
        self._start = start
        self._last  = self._start + span_ms

    def get_start(self):
        """Get start timestamp"""
        return self._start

    def get_end(self):
        """Get end timestamp"""
        return self._last

    def __str__(self):  # pragma: no cover
        return "[%s, %s]" % (self._start, self._last)
