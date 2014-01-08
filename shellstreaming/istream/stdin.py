# -*- coding: utf-8 -*-
"""
    shellstreaming.istream.stdin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Infinite input stream from stdin
"""
from relshell.record import Record
from relshell.recorddef import RecordDef
from shellstreaming.istream.base import Base


class Stdin(Base):
    """Infinite input stream from stdin"""
    def __init__(self, **kw):
        """Constructor
        """
        Base.__init__(self, **kw)

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
