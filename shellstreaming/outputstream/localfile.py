# -*- coding: utf-8 -*-
"""
    shellstreaming.outputstream.localfile
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Output records into local file
"""
from shellstreaming.outputstream.base import Base


class LocalFile(Base):
    """Output records into local file"""

    def __init__(self, path, **kw):
        """Setup outputstream

        :param path: path to output file (overwritten)
        :param **kw: passed to :func:`Base.__init__()`
        """
        Base.__init__(self, **kw)
        self._f = open(path, 'w')

    def __del__(self):
        self._f.close()

    def run(self):
        """Output batch into local file
        """
        while True:
            batch = self._batch_q.pop()
            if batch is None:
                break
            # [fix] - how about output format?????
            self._f.write(str(batch))
            self._f.flush()
