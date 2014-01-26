# -*- coding: utf-8 -*-
import nose.tools as ns
from shellstreaming.core.batch import Batch
from relshell.recorddef import RecordDef
from relshell.record import Record
from shellstreaming.core.batch_queue import BatchQueue
from shellstreaming.operator.count_window import CountWindow


RDEF = RecordDef([{'name': 'col0', 'type': 'INT'}])


def _create_test_batch():
    return Batch(RDEF, (Record(1), Record(2), Record(3)))


def test_count_window_usage():
    # prepare input/output queue
    in_q, out_q = (BatchQueue(), BatchQueue())
    in_q.push(_create_test_batch())
    in_q.push(None)

    win = CountWindow(size=2, input_queues={'a': in_q}, output_queues={'b': out_q})
    win.join()

    ns.eq_(out_q.pop(), Batch(RDEF, (           Record(1),)))
    ns.eq_(out_q.pop(), Batch(RDEF, (Record(1), Record(2))))
    ns.eq_(out_q.pop(), Batch(RDEF, (Record(2), Record(3))))
    ns.ok_(out_q.pop() is None)


def test_multiple_batch_input():
    # prepare input/output queue
    in_q, out_q = (BatchQueue(), BatchQueue())
    in_q.push(_create_test_batch())
    in_q.push(_create_test_batch())
    in_q.push(None)

    win = CountWindow(size=2, input_queues={'a': in_q}, output_queues={'b': out_q})
    win.join()

    ns.eq_(out_q.pop(), Batch(RDEF, (           Record(1),)))
    ns.eq_(out_q.pop(), Batch(RDEF, (Record(1), Record(2))))
    ns.eq_(out_q.pop(), Batch(RDEF, (Record(2), Record(3))))
    ns.eq_(out_q.pop(), Batch(RDEF, (Record(3), Record(1))))
    ns.eq_(out_q.pop(), Batch(RDEF, (Record(1), Record(2))))
    ns.eq_(out_q.pop(), Batch(RDEF, (Record(2), Record(3))))
    ns.ok_(out_q.pop() is None)


def test_slide_size():
    # prepare input/output queue
    in_q, out_q = (BatchQueue(), BatchQueue())
    in_q.push(_create_test_batch())
    in_q.push(_create_test_batch())
    in_q.push(None)

    win = CountWindow(size=2, slide_size=2,
                      input_queues={'a': in_q}, output_queues={'b': out_q})
    win.join()

    ns.eq_(out_q.pop(), Batch(RDEF, (Record(1), Record(2))))
    ns.eq_(out_q.pop(), Batch(RDEF, (Record(3), Record(1))))
    ns.eq_(out_q.pop(), Batch(RDEF, (Record(2), Record(3))))
    ns.ok_(out_q.pop() is None)
