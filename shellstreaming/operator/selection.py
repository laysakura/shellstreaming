# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.selection
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides filtering operators
"""
from Queue import Queue
from shellstreaming.batch import Batch
from shellstreaming.error import OperatorInitError
from shellstreaming.operator.base import Base


class Selection(Base):
    """Filtering operator"""
    match_op = [
        '=', '!='
    ]
    """Match operators"""

    range_op = [
        '<', '>', '<=', '>='
    ]
    """Range operators"""

    def __init__(self, column_index, op1, val1, op2=None, val2=None):
        """Creates various kinds of selection operators.

        `match operators <#shellstreaming.operator.Selection.match_op>`_ and
        `range operators <#shellstreaming.operator.Selection.range_op>`_
        can be used.

        Works like SQL's ``where col_val <op1> val1  [and col_val <op2> val2]`` clause.

        :param column_index: index of column to filter
        :param op1:  one of `match operators <#shellstreaming.operator.Selection.match_op>`_ or
            `range operators <#shellstreaming.operator.Selection.range_op>`_
        :param val1: used like `col <op1> val1`
        :param op2:
            `<` or `<=`
                when `op1` is either of `>` or `>=`
            `None`
                otherwise
        :param val2: used like `col <op1> val1 and col <op2> val2`
        :raises: `OperatorInitError <#shellstreaming.error.OperatorInitError>`_ when `op1` and `op2` are invalid.
        """
        Selection._chk_valid_ops(op1, op2)

        self._col = column_index
        self._op1, self._val1 = (op1, val1)
        self._op2, self._val2 = (op2, val2)
        Base.__init__(self)

    def execute(self, batch):
        """Match-filters records

        :param batch: batch to filter
        :returns:     batch w/ filtered records
        """
        q = Queue()
        for rec in batch:
            if Selection._cmp(rec[self._col], self._op1, self._val1, self._op2, self._val2):
                q.put(rec)
        return Batch(batch.timespan, q)  # TODO: is it OK to always use timestamp from inputstream?

    # private functions
    @staticmethod
    def _chk_valid_ops(op1, op2):
        if op1 not in Selection.match_op and op1 not in Selection.range_op:
            raise OperatorInitError('`op1` is invalid: %s' % (op1))

        if op1 in ('=', '!=', '<', '<='):
            if op2 is not None: raise OperatorInitError('`op2` must be `None` when `op1` is `%s`' % (op1))
        elif op1 in ('>', '>='):
            if op2 not in (None, '<', '<='): raise OperatorInitError('`op2` must be `<` or `<=` when `op1` is `%s`' % (op1))

    @staticmethod
    def _cmp(col_val, op1, val1, op2, val2):
        """Compare

        ``col_val <op1> val1  [and col_val <op2> val2]``
        """
        assert(op1 in Selection.match_op or op1 in Selection.range_op)
        if   op1 == '='  : return col_val == val1
        elif op1 == '!=' : return col_val != val1
        elif op1 == '<'  : return col_val <  val1
        elif op1 == '<=' : return col_val <= val1
        elif op1 == '>':
            if op2 is None: return col_val > val1
            assert(op2 in ('<', '<='))
            if   op2 == '<' : return val1 < col_val <  val2
            elif op2 == '<=': return val1 < col_val <= val2
        elif op1 == '>=':
            if op2 is None: return col_val >= val1
            assert(op2 in ('<', '<='))
            if   op2 == '<' : return val1 <= col_val <  val2
            elif op2 == '<=': return val1 <= col_val <= val2
