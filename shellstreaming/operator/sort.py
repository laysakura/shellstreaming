# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.sort
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides sort operators
"""
from shellstreaming.batch import Batch
from shellstreaming.error import OperatorInitError
from shellstreaming.operator.base import Base


# TODO: top-k algorithm?
class Sort(Base):
    """Sort operator"""

    def __init__(self, column_index, desc=False):
        """Creates sort operators.

        Works like SQL's ``order by [desc] col_val``.

        :param column_index: index of column to filter
        :param desc:         sort in reverse order when `True`
        """
        self._col  = column_index
        self._desc = desc
        Base.__init__(self)

    def execute(self, batch):
        """Sort records

        :param batch: batch to sort
        :returns:     sorted batch
        """
        records = []
        for rec in batch:
            records.append(rec)
        records.sort(
            cmp=lambda rec_x, rec_y: cmp(rec_x[self._col], rec_y[self._col]),
            reverse=self._desc
        )  # TODO: faster algorithm. E.g. keep sorted order when inserting
        return Batch(batch.timespan, tuple(records))  # TODO: is it OK to always use timestamp from inputstream?
