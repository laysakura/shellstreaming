# -*- coding: utf-8 -*-
"""
    shellstreaming.inputstream.stdin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Infinite input stream from stdin
"""
from relshell.record import Record
from relshell.recorddef import RecordDef
from shellstreaming.inputstream.base import Base


class Stdin(Base):
    """Infinite input stream from stdin"""
    def __init__(self, batch_span_ms=1000):
        """Constructor

        :param batch_span_ms: time span to assemble records as batch
        """
        Base.__init__(self, batch_span_ms)

    def run(self):
        rdef = RecordDef([{'name': 'line', 'type': 'STRING'}])
        while True:
            if self.interrupted():
                break

            # sys.stderr.write('Enter record contents: ')
            try:
                line = raw_input().rstrip('\r\n')
                self.add(rdef, Record(line))
            except EOFError:
                continue
