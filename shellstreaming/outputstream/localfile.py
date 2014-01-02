# -*- coding: utf-8 -*-
"""
    shellstreaming.outputstream.localfile
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Output records into local file
"""


class LocalFile(object):
    """Output records into local file"""

    def __init__(self, path):
        """Setup outputstream

        :param path: path to output file (overwritten)
        """
        self._f = open(path, 'w')

    def __del__(self):
        self._f.close()

    def write(self, batch):
        """Output batch into local file
        """
        # [fix] - how about output format?????
        self._f.write(str(batch))
        self._f.flush()
