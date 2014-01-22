# -*- coding: utf-8 -*-
"""
    shellstreaming.istream.textfile
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: FiniteStream for text files.

    A line is used as record with single column.
"""
from relshell.record import Record
from relshell.recorddef import RecordDef
from shellstreaming.istream.base import Base


class TextFile(Base):
    """FiniteStream for text files"""
    def __init__(self, path, records_in_batch=100, **kw):
        """Constructor

        :param path:          path to text file
        """
        self._path = path
        Base.__init__(self, records_in_batch=records_in_batch, **kw)

    def run(self):
        """Reads a text file line-by-line until EOF"""
        with open(self._path) as f:
            rdef = RecordDef([{'name': 'line', 'type': 'STRING'}])
            for line in f:
                if self._interrupted():
                    break
                self.add(rdef, Record(line))
        self.add(rdef, None)  # producer has end data-fetching
