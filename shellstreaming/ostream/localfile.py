# -*- coding: utf-8 -*-
"""
    shellstreaming.ostream.localfile
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Output records into local file
"""
from shellstreaming.ostream.base import Base


class LocalFile(Base):
    """Output records into local file"""

    def __init__(self, path, **kw):
        """Setup ostream

        :param path: path to output file (overwritten)
        :param **kw: passed to :func:`Base.__init__()`
        """
        self._f = open(path, 'w')
        Base.__init__(self, **kw)

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