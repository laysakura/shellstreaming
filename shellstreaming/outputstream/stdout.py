# -*- coding: utf-8 -*-
"""
    shellstreaming.outputstream.stdout
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Output records to stdout
"""
from shellstreaming.outputstream.base import Base


class Stdout(Base):
    """Output records to stdout"""

    def run(self):
        """Output batch to stdout"""
        while True:
            batch = self._batch_q.pop()
            if batch is None:
                break
            # [fix] - how about output format?????
            print(str(batch))
