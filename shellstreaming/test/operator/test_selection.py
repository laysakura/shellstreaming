# -*- coding: utf-8 -*-
from nose.tools import *
from Queue import Queue
from datetime import datetime
from shellstreaming.batch import Batch
from shellstreaming.recorddef import RecordDef
from shellstreaming.record import Record
from shellstreaming.timespan import Timespan
from shellstreaming.timestamp import Timestamp
from shellstreaming.error import OperatorInitError
from shellstreaming.operator.selection import Selection


def _create_test_batch():
    rdef = RecordDef([
        {'name': 'col0', 'type': 'INT'},
        {'name': 'col1', 'type': 'STRING'},
    ])
    q = Queue()
    q.put(Record(rdef, 123, 'aaa'))
    q.put(Record(rdef, 777, 'aaa'))
    q.put(Record(rdef, 333, 'bbb'))
    q.put(Record(rdef, 777, 'bbb'))
    return Batch(Timespan(Timestamp(datetime.now()), 10), q)


def test_selection_usage():
    batch = _create_test_batch()

    op = Selection(0, op1='=', val1=777)
    filtered_batch = op.execute(batch)
    n = 0
    for record in filtered_batch:
        n += 1
    eq_(n, 2)


def test_selection_closed_range():
    batch = _create_test_batch()

    op = Selection(0, op1='>', val1=123, op2='<=', val2=777)
    filtered_batch = op.execute(batch)
    n = 0
    for record in filtered_batch:
        n += 1
    eq_(n, 3)


def test_selection_cascade():
    batch = _create_test_batch()

    op0 = Selection(0, op1='>=', val1=333)
    op1 = Selection(1, op1='=', val1='aaa')

    batch = op0.execute(batch)
    batch = op1.execute(batch)

    n = 0
    for record in batch:
        n += 1
    eq_(n, 1)


@raises(OperatorInitError)
def test_selection_invalid_operator1():
    Selection(0, '==', 777)  # '=' is correct


@raises(OperatorInitError)
def test_selection_invalid_operator2():
    Selection(0, '=', 777, '<', 999)  # `op2` can be only defined when `op1` is range op.


@raises(OperatorInitError)
def test_selection_invalid_operator3():
    Selection(0, '>=', 777, '=', 999)  # `op2` has to have opposite range


@raises(OperatorInitError)
def test_selection_invalid_operator4():
    Selection(0, '<', 777, '>', 333)  # `op1` has to be `>` or `>=` to use `op2`
