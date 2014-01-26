# -*- coding: utf-8 -*-
"""
    shellstreaming.ostream.localfile
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Output records into local file
"""
from shellstreaming.ostream.io_stream import IoStream


class LocalFile(IoStream):
    """Output records into local file"""

    def __init__(self, path, **kw):
        """Setup ostream

        :param path: path to output file (overwritten)
        :param **kw: passed to :func:`Base.__init__()`
        """
        self._f = open(path, 'a')
        IoStream.__init__(self, self._f, **kw)

    def __del__(self):
        self._f.close()
