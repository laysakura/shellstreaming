# -*- coding: utf-8 -*-
"""
    shellstreaming.istream.incint
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Generates incremented integer sequence.

    Mainly for testing purpose
"""
import time
from relshell.record import Record
from relshell.recorddef import RecordDef
from shellstreaming.istream.base import Base


class IncInt(Base):
    """Infinite input stream which generates random integer sequence"""
    def __init__(self, sleep_sec=1e-3, **kw):
        """Constructor
        """
        self._cnt       = 0
        self._sleep_sec = sleep_sec
        Base.__init__(self, **kw)

    def run(self):
        rdef = RecordDef([{'name': 'num', 'type': 'INT'}])
        while True:
            time.sleep(self._sleep_sec)
            if self._interrupted():
                break
            self.add(rdef, Record(self._cnt))
            self._cnt += 1
