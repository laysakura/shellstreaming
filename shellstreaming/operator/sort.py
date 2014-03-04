# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.sort
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides sort operators
"""
from shellstreaming.core.batch import Batch
from shellstreaming.operator.base import Base


# [todo] - top-k algorithm?
class Sort(Base):
    """Sort operator"""

    def __init__(self, column_name, desc=False, **kw):
        """Creates sort operators.

        Works like SQL's ``order by [desc] col_val``.

        :param column_name: name of column to be sort key
        :param desc:      sort in reverse order when `True`
        """
        self._colname = column_name
        self._desc    = desc

        in_qs, out_qs = (kw['input_queues'], kw['output_queues'])
        # input queue
        assert(len(in_qs) == 1)
        self._in_q = in_qs.values()[0]
        # output queues
        assert(len(out_qs) == 1)
        self._out_q = out_qs.values()[0]

        Base.__init__(self)

    def run(self):
        """Sort records
        """
        while True:
            batch = self._in_q.pop()
            if batch is None:
                self._out_q.push(None)
                break

            rdef   = batch.record_def()
            colidx = rdef.colindex_by_colname(self._colname)
            sorted_rec = sorted(
                batch._records, reverse=self._desc,
                cmp=lambda rec_x, rec_y: cmp(rec_x[colidx], rec_y[colidx]),
            )
            out_batch = Batch(batch.record_def(), tuple(sorted_rec))
            self._out_q.push(out_batch)

    @staticmethod
    def out_stream_edge_id_suffixes(args):
        return ('sorted', )
