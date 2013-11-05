# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.selection
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides match selection & range selection operators
"""
from Queue import Queue
from shellstreaming.batch import Batch
from shellstreaming.operator.base import Base


class MatchSelection(Base):
    """Match selection operator"""
    def __init__(self, column_index, value_to_match):
        """Constructor.

        Works like SQL's ``where column = value_to_match``.

        :param column_index:   index of column
        :param value_to_match: value to match
        """
        self._col = column_index
        self._val = value_to_match
        Base.__init__(self)

    def execute(self, batch):
        """Match-filters records

        :param batch: batch to filter
        :returns:     batch w/ filtered records
        """
        q = Queue()
        for rec in batch:
            if rec[self._col] == self._val:
                q.put(rec)
        return Batch(batch.timespan, q)  # TODO: is it OK to always use timestamp from inputstream?
