# -*- coding: utf-8 -*-
from nose.tools import *
from Queue import Queue
from datetime import datetime
from shellstreaming.timestamp import Timestamp
from shellstreaming.timespan import Timespan
from shellstreaming.record import Record
from shellstreaming.recorddef import RecordDef
from shellstreaming.error import TimestampError
from shellstreaming.batch import Batch


def test_batch_timestamp_check_ok():
    t     = Timestamp(datetime.now())
    tspan = Timespan(t, 10)
    rdef  = RecordDef([{'name': 'col0', 'type': 'INT'}])

    q = Queue()
    q.put(Record(rdef, 123, timestamp=t))
    q.put(Record(rdef, 123, timestamp=t + 5))
    q.put(Record(rdef, 123, timestamp=t + 10))
    q.put(None)  # `record_q` argument of `Batch` must have None as last element

    batch = Batch(tspan, q, timestamp_check=True)


@raises(TimestampError)
def test_batch_timestamp_check_ng():
    t     = Timestamp(datetime.now())
    tspan = Timespan(t, 10)
    rdef  = RecordDef([{'name': 'col0', 'type': 'INT'}])

    q = Queue()
    q.put(Record(rdef, 123, timestamp=t))
    q.put(Record(rdef, 123, timestamp=t - 3))  # NG!
    q.put(Record(rdef, 123, timestamp=t + 10))
    q.put(None)  # `record_q` argument of `Batch` must have None as last element

    batch = Batch(tspan, q, timestamp_check=True)
