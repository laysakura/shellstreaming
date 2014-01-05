# -*- coding: utf-8 -*-
"""
    shellstreaming.outputstream.stdout
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Output records to stdout
"""


class Stdout(object):  # [fix] - ostreamも何かinterface継承
    """Output records to stdout"""

    def __init__(self):
        """Setup outputstream"""

    def write(self, batch):
        """Output batch to stdout"""
        # [fix] - how about output format?????
        print(str(batch))
