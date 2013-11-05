# -*- coding: utf-8 -*-
from nose.tools import *
from Queue import Queue
from datetime import datetime
from shellstreaming.batch import Batch
from shellstreaming.recorddef import RecordDef
from shellstreaming.record import Record
from shellstreaming.timespan import Timespan
from shellstreaming.timestamp import Timestamp
from shellstreaming.operator.selection import MatchSelection


def _create_test_batch():
    rdef = RecordDef([{'name': 'col0', 'type': 'INT'}])
    q = Queue()
    q.put(Record(rdef, 123))
    q.put(Record(rdef, 777))
    q.put(Record(rdef, 333))
    q.put(Record(rdef, 777))
    q.put(None)
    return Batch(Timespan(Timestamp(datetime.now()), 10), q)


def test_match_selection_usage():
    batch = _create_test_batch()

    op = MatchSelection(0, 777)
    filtered_batch = op.execute(batch)
    n = 0
    for record in filtered_batch:
        n += 1
    eq_(n, 2)
