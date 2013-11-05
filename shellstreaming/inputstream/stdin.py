# -*- coding: utf-8 -*-
"""
    shellstreaming.inputstream.stdin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Infinite input stream from stdin
"""
import sys
from shellstreaming.inputstream.base import InfiniteStream
from shellstreaming.record import Record
from shellstreaming.recorddef import RecordDef


class Stdin(InfiniteStream):
    """Infinite input stream from stdin"""
    def __init__(self, batch_span_ms=1000):
        """Constructor

        :param batch_span_ms: time span to assemble records as batch
        """
        InfiniteStream.__init__(self, batch_span_ms)

    def run(self):
        rdef = RecordDef([{'name': 'line', 'type': 'STRING'}])
        while True:
            if self.interrupted():
                break

            # sys.stderr.write('Enter record contents: ')
            try:
                line = raw_input().rstrip('\r\n')
                self.add(Record(rdef, line))
            except EOFError as e:
                continue
