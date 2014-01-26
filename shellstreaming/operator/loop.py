# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.loop
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: operator for benchmark
"""
from shellstreaming.operator.base import Base


class Loop(Base):
    """"""

    def __init__(self, **kw):
        """"""
        in_qs, out_qs = (kw['input_queues'], kw['output_queues'])
        # input queue
        assert(len(in_qs) == 1)
        self._in_q = in_qs.values()[0]
        # output queues
        assert(len(out_qs) == 1)
        self._out_q = out_qs.values()[0]

        Base.__init__(self)

    def run(self):
        """
        """
        while True:
            batch = self._in_q.pop()
            if batch is None:
                self._out_q.push(None)
                break

            i = 0
            for _ in xrange(3000000):
                i += 1

    @staticmethod
    def out_stream_edge_id_suffixes(args):
        return ('loop', )
