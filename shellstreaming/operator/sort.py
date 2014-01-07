# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.sort
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides sort operators
"""
from relshell.batch import Batch
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
        assert(len(out_qs) == 1)
        self._out_q = out_qs.values()[0]

        Base.__init__(self, **kw)

    def run(self):
        """Sort records
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
            out_batch = Batch(batch.record_def(), tuple(sorted_rec))
            self._out_q.push(out_batch)

    @staticmethod
    def out_stream_edge_id_suffixes():
        return ('sorted', )
