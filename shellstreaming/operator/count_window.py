# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.count_window
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides cout window
"""
# standard module
from collections import deque

# my module
from shellstreaming.core.batch import Batch
from shellstreaming.operator.base import Base


class CountWindow(Base):  # [todo] - inherit common `Window` class?
    """Count window operator"""

    def __init__(self, size, slide_size=1, **kw):
        """Creates sort operators.

        Works like SQL's ``order by [desc] col_val``.

        :param size:       output batch size (num of records)
        :param slide_size: trigger to output batch. When `slide_size=2`,
            :class:`CountWindow` operator waits 2 records and then outputs recent batches.
            :param:`slide_size` must be no greater than :param:`size`.
            (example)
        :raises: `ValueError` when :param:`slide_size` > :param:`size`
        """
        if slide_size > size:
            raise ValueError('slide_size > size !!')

        self._sz       = size
        self._slide_sz = slide_size

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
        win       = deque(maxlen=self._sz)
        slide_cnt = 0  # output batch when `slide_cnt == self._slide_sz`
        while True:
            batch = self._in_q.pop()
            if batch is None:
                self._out_q.push(None)  # [todo] - pushing `None` when finish op is not a bad idea.
                                        # [todo] - but sending 'punctuation' is more general.
                                        # [todo] - see: http://pic.dhe.ibm.com/infocenter/streams/v2r0/index.jsp?topic=%2Fcom.ibm.swg.im.infosphere.streams.spl-language-specification.doc%2Fdoc%2Fpunctuation.html
                break

            for rec in batch:
                win.append(rec)
                slide_cnt += 1
                if slide_cnt == self._slide_sz:
                    self._out_q.push(Batch(batch.record_def(), tuple(win)))
                    slide_cnt = 0

    @staticmethod
    def out_stream_edge_id_suffixes(args):
        return ('window', )
