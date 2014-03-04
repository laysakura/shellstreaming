# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.external_time_window
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides timestamp window
"""
# standard module

# my module
from shellstreaming.core.batch import Batch
from relshell.timespan import Timespan
from shellstreaming.operator.base import Base


class ExternalTimeWindow(Base):  # [todo] - inherit common `Window` class?
    """Count window operator"""

    def __init__(
        self,
        timestamp_column,
        latest_timestamp=None,
        # [todo] - add `size_secs`, ...
        size_days=None,
        output_per_records=1,
        **kw
    ):
        """
        """
        assert(latest_timestamp is not None)  # [fix] - use timestamp each time new batch arrives when this is None
        assert(size_days is not None)  # [todo] - only one of size_days, size_hours, ... is not None

        self._ts_col = timestamp_column

        size_sec    = long(size_days * 24 * 60 * 60)
        self._tspan = Timespan(latest_timestamp - size_sec, size_sec)

        self._output_per_rec = output_per_records

        in_qs, out_qs = (kw['input_queues'], kw['output_queues'])
        # input queue
        assert(len(in_qs) == 1)
        self._in_q = in_qs.values()[0]
        # output queues
        assert(len(out_qs) == 1)
        self._out_q = out_qs.values()[0]

        Base.__init__(self)

    def run(self):
        """"""
        win       = []
        slide_cnt = 0  # output batch when `slide_cnt == self._output_per_rec`
        while True:
            batch = self._in_q.pop()
            if batch is None:
                self._out_q.push(None)
                break

            # insert record into window if appropreate
            rdef   = batch.record_def()
            ts_idx = rdef.colindex_by_colname(self._ts_col)
            for rec in batch:
                ts = rec[ts_idx]
                if ts.between(self._tspan):
                    win.append(rec)
                    slide_cnt += 1

                # output batch when demanded
                if slide_cnt == self._output_per_rec:
                    self._out_q.push(Batch(rdef, tuple(win)))
                    slide_cnt = 0

    @staticmethod
    def out_stream_edge_id_suffixes(args):
        return ('window', )
