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
    def __init__(self, **kw):
        """Constructor
        """
        self._cnt = 0
        Base.__init__(self, **kw)

    def run(self):
        rdef = RecordDef([{'name': 'num', 'type': 'INT'}])
        while True:
            time.sleep(0.001)
            if self._interrupted():
                break
            self.add(rdef, Record(self._cnt))
            self._cnt += 1
