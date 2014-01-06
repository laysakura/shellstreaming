# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.sort
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides sort operators
"""
from shellstreaming.timed_batch import TimedBatch
from shellstreaming.operator.base import Base


# [todo] - top-k algorithm?
class Sort(Base):
    """Sort operator"""

    def __init__(self, column_index, desc=False, **kw):
        """Creates sort operators.

        Works like SQL's ``order by [desc] col_val``.

        :param column_index: index of column to filter
        :param desc:         sort in reverse order when `True`
        """
        self._col  = column_index
        self._desc = desc

        in_qs, out_qs = (kw['input_queues'], kw['output_queues'])
        # input queue
        assert(len(in_qs) == 1)
        self._in_q = in_qs.values()[0]
        # output queues
        assert(len(out_qs) == 1 and 'sorted' in out_qs)
        self._out_q = out_qs['sorted']

        Base.__init__(self, **kw)

    def run(self):
        """Sort records

        :param batch: batch to sort
        :returns:     sorted batch
        """
        while True:
            batch = self._in_q.pop()
            if batch is None:
                self._out_q.push(None)
                break

            sorted_rec = sorted(
                batch._records, reverse=self._desc,
                cmp=lambda rec_x, rec_y: cmp(rec_x[self._col], rec_y[self._col]),
            )
            out_batch = TimedBatch(batch.timespan, tuple(sorted_rec))  # [todo] - is it OK to always use timestamp from inputstream?
            self._out_q.push(out_batch)

    @staticmethod
    def out_stream_edge_id_suffixes():
        return ('sorted', )
