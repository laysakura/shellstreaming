# -*- coding: utf-8 -*-
"""
    shellstreaming.timestamp
    ~~~~~~~~~~~~~~~~~~~~~~~~
"""
import datetime


class Timestamp(object):
    def __init__(self, timestamp=datetime.datetime.now()):
        # year=2013, month=10, day=29, hour=01, minute=04, second=12, microsecond=123456
        # => 20131029010412123456
        t = timestamp
        self._ts = int((t.microsecond) + (t.second * 1e6) + (t.minute * 1e8) + (t.hour * 1e10) +
                       (t.day * 1e12)  + (t.month * 1e14) + (t.year * 1e16))

    def year(self):
        return int(str(self._ts)[0:4])

    def month(self):
        return int(str(self._ts)[4:6])

    def day(self):
        return int(str(self._ts)[6:8])

    def hour(self):
        return int(str(self._ts)[8:10])

    def minute(self):
        return int(str(self._ts)[10:12])

    def second(self):
        return int(str(self._ts)[12:14])

    def microsecond(self):
        return int(str(self._ts)[14:20])

    def datetime(self):
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
        return Timestamp(timestamp=self.datetime() + datetime.timedelta(microseconds=ms * 1e3))

    def __sub__(self, ms):
        return Timestamp(timestamp=self.datetime() - datetime.timedelta(microseconds=ms * 1e3))

    def __int__(self):
        return int(self._ts)

    def __str__(self):
        t = str(self._ts)
        return "%04d_%02d_%02d__%02d_%02d_%02d_%06d" % (
            self.year(), self.month(),  self.day(),
            self.hour(), self.minute(), self.second(),
            self.microsecond())
