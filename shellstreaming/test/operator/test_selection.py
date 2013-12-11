# -*- coding: utf-8 -*-
from nose.tools import *
from datetime import datetime
from shellstreaming.timed_batch import TimedBatch
from relshell.recorddef import RecordDef
from shellstreaming.timed_record import TimedRecord
from shellstreaming.timespan import Timespan
from shellstreaming.timestamp import Timestamp
from shellstreaming.error import OperatorInitError
from shellstreaming.operator.selection import Selection


def _create_test_batch():
    rdef = RecordDef([
        {'name': 'col0', 'type': 'INT'},
        {'name': 'col1', 'type': 'STRING'},
    ])
    return TimedBatch(
        Timespan(Timestamp(datetime.now()), 10),
        (
            TimedRecord(rdef, 123, 'aaa'),
            TimedRecord(rdef, 777, 'aaa'),
            TimedRecord(rdef, 333, 'bbb'),
            TimedRecord(rdef, 777, 'bbb'),
        ))


def test_selection_usage():
    batch = _create_test_batch()

    op = Selection(0, op1='=', val1=777)
    filtered_batch = op.execute(batch)
    n = 0
    for record in filtered_batch:
        n += 1
    eq_(n, 2)


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


def test_selection_all_match_op():
    op    = Selection(0, op1='=', val1=333)
    batch = op.execute(_create_test_batch())
    n = 0
    for record in batch: n += 1
    eq_(n, 1)

    op    = Selection(0, op1='!=', val1=333)
    batch = op.execute(_create_test_batch())
    n = 0
    for record in batch: n += 1
    eq_(n, 3)


def test_selection_all_range_op():
    op    = Selection(0, op1='>', val1=333)
    batch = op.execute(_create_test_batch())
    n = 0
    for record in batch: n += 1
    eq_(n, 2)

    op    = Selection(0, op1='>=', val1=333)
    batch = op.execute(_create_test_batch())
    n = 0
    for record in batch: n += 1
    eq_(n, 3)

    op    = Selection(0, op1='<', val1=333)
    batch = op.execute(_create_test_batch())
    n = 0
    for record in batch: n += 1
    eq_(n, 1)

    op    = Selection(0, op1='<=', val1=333)
    batch = op.execute(_create_test_batch())
    n = 0
    for record in batch: n += 1
    eq_(n, 2)


def test_selection_all_closed_range():
    op = Selection(0, op1='>', val1=123, op2='<', val2=777)
    batch = op.execute(_create_test_batch())
    n = 0
    for record in batch: n += 1
    eq_(n, 1)

    op = Selection(0, op1='>', val1=123, op2='<=', val2=777)
    batch = op.execute(_create_test_batch())
    n = 0
    for record in batch: n += 1
    eq_(n, 3)

    op = Selection(0, op1='>=', val1=123, op2='<', val2=777)
    batch = op.execute(_create_test_batch())
    n = 0
    for record in batch: n += 1
    eq_(n, 2)

    op = Selection(0, op1='>=', val1=123, op2='<=', val2=777)
    batch = op.execute(_create_test_batch())
    n = 0
    for record in batch: n += 1
    eq_(n, 4)


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
