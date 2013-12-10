# -*- coding: utf-8 -*-
from nose.tools import *
from datetime import datetime
from relshell.recorddef import RecordDef
from shellstreaming.timestamp import Timestamp
from shellstreaming.timespan import Timespan
from shellstreaming.timed_record import TimedRecord
from shellstreaming.error import TimestampError
from shellstreaming.timed_batch import TimedBatch


def test_batch_timestamp_check_ok():
    t     = Timestamp(datetime.now())
    tspan = Timespan(t, 10)
    rdef  = RecordDef([{'name': 'col0', 'type': 'INT'}])
    batch = TimedBatch(
        tspan,
        (
            TimedRecord(rdef, 123, timestamp=t),
            TimedRecord(rdef, 123, timestamp=t + 5),
            TimedRecord(rdef, 123, timestamp=t + 10),
        ),
        timestamp_check=True)


@raises(TimestampError)
def test_batch_timestamp_check_ng():
    t     = Timestamp(datetime.now())
    tspan = Timespan(t, 10)
    rdef  = RecordDef([{'name': 'col0', 'type': 'INT'}])
    batch = TimedBatch(
        tspan,
        (
            TimedRecord(rdef, 123, timestamp=t),
            TimedRecord(rdef, 123, timestamp=t - 3),  # NG!
            TimedRecord(rdef, 123, timestamp=t + 10),
        ),
        timestamp_check=True)
