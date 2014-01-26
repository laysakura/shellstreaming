# -*- coding: utf-8 -*-
"""
    shellstreaming.ostream.null
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: ignore output records (for performance evaluation purpose)
"""
from shellstreaming.ostream.base import Base


class Null(Base):
    """"""

    def __init__(self, **kw):
        """"""
        Base.__init__(self, **kw)

    def run(self):
        """Output batch to nowhere"""
        while True:
            batch = self._batch_q.pop()
            if batch is None:
                break
