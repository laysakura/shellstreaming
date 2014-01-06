# -*- coding: utf-8 -*-
"""
    shellstreaming.inputstream.textfile
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: FiniteStream for text files.

    A line is used as record with single column.
"""
from relshell.record import Record
from relshell.recorddef import RecordDef
from shellstreaming.inputstream.base import Base


class TextFile(Base):
    """FiniteStream for text files"""
    def __init__(self, path, output_queue, batch_span_ms=1000):
        """Constructor

        :param path:          path to text file
        :param batch_span_ms: time span to assemble records as batch
        """
        self._path = path
        Base.__init__(self, output_queue, batch_span_ms)

    def run(self):
        """Reads a text file line-by-line until EOF"""
        with open(self._path) as f:
            rdef = RecordDef([{'name': 'line', 'type': 'STRING'}])
            for line in f:
                if self._interrupted():
                    break
                self.add(rdef, Record(line))
        self.add(rdef, None)  # producer has end data-fetching
