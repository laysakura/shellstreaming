# -*- coding: utf-8 -*-
from nose.tools import *
from datetime import datetime
from shellstreaming.batch import Batch
from shellstreaming.recorddef import RecordDef
from shellstreaming.record import Record
from shellstreaming.timespan import Timespan
from shellstreaming.timestamp import Timestamp
from shellstreaming.error import OperatorInitError
from shellstreaming.operator.sort import Sort


def _create_test_batch():
    rdef = RecordDef([
        {'name': 'col0', 'type': 'INT'},
        {'name': 'col1', 'type': 'STRING'},
    ])
    return Batch(
        Timespan(Timestamp(datetime.now()), 10),
        (
            Record(rdef, 123, '101'),
            Record(rdef, 777, '11'),
            Record(rdef, 333, '200'),
            Record(rdef, 777, '30'),
        ))


def test_sort_usage():
    # ascendant order
    op = Sort(0)
    sorted_batch = op.execute(_create_test_batch())
    col0s = []
    for record in sorted_batch:
        col0s.append(record[0])
    eq_(col0s, [123, 333, 777, 777])

    # descendant order
    op = Sort(0, desc=True)
    sorted_batch = op.execute(_create_test_batch())
    col0s = []
    for record in sorted_batch:
        col0s.append(record[0])
    eq_(col0s, [777, 777, 333, 123])


def test_sort_by_string():
    op = Sort(1)
    sorted_batch = op.execute(_create_test_batch())
    col1s = []
    for record in sorted_batch:
        col1s.append(record[1])
    eq_(col1s, ['101', '11', '200', '30'])
