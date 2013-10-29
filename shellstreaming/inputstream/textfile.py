# -*- coding: utf-8 -*-
"""
    shellstreaming.inputstream.textfile
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: FiniteStream for text files.

    A line is used as record with single column.
"""
from shellstreaming.inputstream.base import FiniteStream
from shellstreaming.record import Record


class TextFile(FiniteStream):
    """FiniteStream for text files"""
    def __init__(self, path, batch_span_ms=1000):
        """Constructor

        :param path:          path to text file
        :param batch_span_ms: time span to assemble records as batch
        """
        self._path = path
        FiniteStream.__init__(self, batch_span_ms)

    def run(self):
        """Reads a text file line-by-line until EOF"""
        with open(self._path) as f:
            rdef = [{'name': 'line', 'type': 'STRING'}]
            line = f.readline()
            while line:
                self.add(Record(rdef, line))
                line = f.readline()
        self.finish_fetching()
