# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.copy_split
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis:
"""
# standard modules
import cPickle as pickle

# my modules
from shellstreaming.operator.base import Base


class CopySplit(Base):
    """"""

    def __init__(self, num_copies, **kw):
        """

        :param conditions: tuple of conditions.
            Each condition is simply `eval`ed after replacing column name into actual value.
        """
        self._num_copies = num_copies
        in_qs, out_qs    = (kw['input_queues'], kw['output_queues'])

        # input queue
        assert(len(in_qs) == 1)
        self._in_q = in_qs.values()[0]
        # output queues
        assert(len(out_qs) == num_copies)
        self._out_qs = out_qs.values()

        Base.__init__(self)

    def run(self):
        """Filter batch according to :param:`*conditions`
        """
        while True:
            batch = self._in_q.pop()
            if batch is None:
                map(lambda q: q.push(None), self._out_qs)
                break

            # create batch's deep-copy and push to all
            for q in self._out_qs:
                cp = pickle.dumps(batch)
                cp = pickle.loads(cp)
                q.push(cp)

    @staticmethod
    def out_stream_edge_id_suffixes(num_copies):
        assert(len(num_copies) == 1)
        return ['copy%d' % (i) for i in range(num_copies[0])]
