# -*- coding: utf-8 -*-
"""
    shellstreaming.istream.textfile_tail
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Works like `tail -f`
"""
# standard modules
import time

# my moduels
from relshell.record import Record
from relshell.recorddef import RecordDef
from shellstreaming.istream.base import Base


class TextFileTail(Base):
    """FiniteStream for text files"""
    def __init__(self, path, read_existing_lines=False, sleep_sec=1e-3,
                 records_in_batch=1, **kw):
        """Constructor

        :param path:          path to text file
        """
        self._path                = path
        self._read_existing_lines = read_existing_lines
        self._sleep_sec           = sleep_sec
        Base.__init__(self, records_in_batch=records_in_batch, **kw)

    def run(self):
        """Reads a text file line-by-line until EOF"""
        with open(self._path) as f:
            rdef = RecordDef([{'name': 'line', 'type': 'STRING'}])

            if not self._read_existing_lines:  # go to the end of file
                f.seek(0, 2)

            while True:
                if self._interrupted():
                    self.add(rdef, None)  # producer has end data-fetching
                    return

                curpos = f.tell()
                line = f.readline()
                if line == '':  # EOF
                    f.seek(curpos)
                else:
                    self.add(rdef, Record(line))
                time.sleep(self._sleep_sec)
