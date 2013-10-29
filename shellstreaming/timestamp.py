# -*- coding: utf-8 -*-
"""
    shellstreaming.timestamp
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Provides efficient data structure to represent timestamp
"""
import datetime


class Timestamp(object):
    """Provides efficient data structure to represent timestamp
    """
    def __init__(self, timestamp):
        """Constructor"""
        # year=2013, month=10, day=29, hour=01, minute=04, second=12, microsecond=123456
        # => 20131029010412123456
        t = timestamp
        self._ts = (t.microsecond +
                    int(t.second * 1e6) + int(t.minute * 1e8) + int(t.hour * 1e10) +
                    int(t.day * 1e12)   + int(t.month * 1e14) + int(t.year * 1e16))

    def year(self):
        """Return year"""
        return int(str(self._ts)[0:4])

    def month(self):
        """Return month"""
        return int(str(self._ts)[4:6])

    def day(self):
        """Return day"""
        return int(str(self._ts)[6:8])

    def hour(self):
        """Return hour"""
        return int(str(self._ts)[8:10])

    def minute(self):
        """Return minute"""
        return int(str(self._ts)[10:12])

    def second(self):
        """Return self"""
        return int(str(self._ts)[12:14])

    def microsecond(self):
        """Return microsecond"""
        return int(str(self._ts)[14:20])

    def datetime(self):
        """Return `datetime` object"""
        return datetime.datetime(
            self.year(), self.month(), self.day(),
            self.hour(), self.minute(), self.second(),
            self.microsecond())

    def __eq__(self, other):
        return self._ts == other._ts

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self._ts < other._ts

    def __add__(self, ms):
        """Add `ms` to this timestamp"""
        return Timestamp(timestamp=self.datetime() + datetime.timedelta(microseconds=ms * 1e3))

    def __sub__(self, ms):
        """Subtract `ms` to this timestamp"""
        return Timestamp(timestamp=self.datetime() - datetime.timedelta(microseconds=ms * 1e3))

    def __int__(self):
        """Return int representation of this timestamp"""
        return int(self._ts)

    def __str__(self):
        """Return str representation of this timestamp"""
        t = str(self._ts)
        return "%04d_%02d_%02d__%02d_%02d_%02d_%06d" % (
            self.year(), self.month(),  self.day(),
            self.hour(), self.minute(), self.second(),
            self.microsecond())
