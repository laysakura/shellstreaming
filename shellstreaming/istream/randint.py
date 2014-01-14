# -*- coding: utf-8 -*-
"""
    shellstreaming.istream.randint
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Generates random integer sequence.

    Mainly for testing `InfiniteStream <#shellstreaming.infinitestream.base.Infinitestream>`_
"""
import random
import time
from relshell.record import Record
from relshell.recorddef import RecordDef
from shellstreaming.istream.base import Base


class RandInt(Base):
    """Infinite input stream which generates random integer sequence"""
    def __init__(self, min_int, max_int, sleep_sec=1e-3, **kw):
        """Constructor

        :param min_int:       minimum integer to generate
        :param max_int:       maximum integer to generate
        """
        self._min       = min_int
        self._max       = max_int
        self._sleep_sec = sleep_sec
        Base.__init__(self, **kw)

    def run(self):
        rdef = RecordDef([{'name': 'num', 'type': 'INT'}])
        while True:
            time.sleep(self._sleep_sec)
            if self._interrupted():
                break
            self.add(rdef, Record(random.randint(self._min, self._max)))
