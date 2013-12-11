# -*- coding: utf-8 -*-
"""
    shellstreaming.inputstream.randint
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Generates random integer sequence.

    Mainly for testing `InfiniteStream <#shellstreaming.infinitestream.base.Infinitestream>`_
"""
import random
import time
from shellstreaming.inputstream.base import InfiniteStream
from shellstreaming.timed_record import TimedRecord
from relshell.recorddef import RecordDef


class RandInt(InfiniteStream):
    """Infinite input stream which generates random integer sequence"""
    def __init__(self, min_int, max_int, batch_span_ms=1000):
        """Constructor

        :param min_int:       minimum integer to generate
        :param max_int:       maximum integer to generate
        :param batch_span_ms: time span to assemble records as batch
        """
        self._min = min_int
        self._max = max_int
        InfiniteStream.__init__(self, batch_span_ms)

    def run(self):
        rdef = RecordDef([{'name': 'num', 'type': 'INT'}])
        while True:
            time.sleep(0.001)
            if self.interrupted():
                break
            self.add(TimedRecord(rdef, random.randint(self._min, self._max)))
