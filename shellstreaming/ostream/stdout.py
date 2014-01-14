# -*- coding: utf-8 -*-
"""
    shellstreaming.ostream.stdout
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Output records to stdout
"""
# standard module
import sys

# my module
from shellstreaming.ostream.io_stream import IoStream


class Stdout(IoStream):
    """Output records to stdout"""

    def __init__(self, **kw):
        """"""
        IoStream.__init__(self, sys.stdout, **kw)
