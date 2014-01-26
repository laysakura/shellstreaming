# -*- coding: utf-8 -*-
import nose.tools as ns
from shellstreaming.core.batch import Batch
from relshell.recorddef import RecordDef
from relshell.record import Record
from relshell.timestamp import Timestamp
from shellstreaming.core.batch_queue import BatchQueue
from shellstreaming.operator.external_time_window import ExternalTimeWindow


RDEF = RecordDef([{'name': 'timestamp', 'type': 'TIMESTAMP'}, {'name': 'x'}])


def test_external_time_window_usage():
    ### window between 2013/12/25 12:00:00 - 2014/1/3 12:00:00 will be created

    # prepare batch
    batch = Batch(RDEF, (
        Record(Timestamp('2014-01-03')         , 'x'),  # ok
        Record(Timestamp('2014-01-04')         , 'x'),  # ng: too new timestamp
        Record(Timestamp('2013-12-24')         , 'x'),  # ng: too old timestamp
        Record(Timestamp('2014-01-03 12:00:00'), 'x'),  # ok
        Record(Timestamp('2013-12-24 12:00:00'), 'x'),  # ok
        Record(Timestamp('2014-01-03 12:00:01'), 'x'),  # ng
        Record(Timestamp('2013-12-24 11:59:59'), 'x'),  # ng
    ))

    # prepare input/output queue
    in_q, out_q = (BatchQueue(), BatchQueue())
    in_q.push(batch)
    in_q.push(None)

    win = ExternalTimeWindow(
        timestamp_column='timestamp',
        size_days=10, latest_timestamp=Timestamp('2014-01-03 12:00:00'), output_per_records=1,
        input_queues={'a': in_q}, output_queues={'b': out_q})
    win.join()

    ns.eq_(out_q.pop(), Batch(RDEF, (
        Record(Timestamp('2014-01-03')         , 'x'),
    )))
    ns.eq_(out_q.pop(), Batch(RDEF, (
        Record(Timestamp('2014-01-03')         , 'x'),
        Record(Timestamp('2014-01-03 12:00:00'), 'x'),
    )))
    ns.eq_(out_q.pop(), Batch(RDEF, (
        Record(Timestamp('2014-01-03')         , 'x'),
        Record(Timestamp('2014-01-03 12:00:00'), 'x'),
        Record(Timestamp('2013-12-24 12:00:00'), 'x'),
    )))
    ns.ok_(out_q.pop() is None)
