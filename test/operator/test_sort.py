# -*- coding: utf-8 -*-
import nose.tools as ns
from shellstreaming.core.batch import Batch
from relshell.recorddef import RecordDef
from relshell.record import Record
from shellstreaming.core.batch_queue import BatchQueue
from shellstreaming.operator.sort import Sort


def _create_test_batch():
    rdef = RecordDef([
        {'name': 'col0', 'type': 'INT'},
        {'name': 'col1', 'type': 'STRING'},
    ])
    return Batch(
        rdef,
        (
            Record(123, '101'),
            Record(777, '11'),
            Record(333, '200'),
            Record(777, '30'),
        ))


def test_sort_usage():
    in_q, out_q = (BatchQueue(), BatchQueue())
    in_q.push(_create_test_batch())
    in_q.push(None)

    # ascendant order
    op = Sort('col0', input_queues={'a': in_q}, output_queues={'b': out_q})
    op.join()
    sorted_batch = out_q.pop()
    col0s = []
    for record in sorted_batch:
        col0s.append(record[0])
    ns.eq_(col0s, [123, 333, 777, 777])


def test_sort_desc():
    in_q, out_q = (BatchQueue(), BatchQueue())
    in_q.push(_create_test_batch())
    in_q.push(None)

    # descendant order
    op = Sort('col0', desc=True, input_queues={'a': in_q}, output_queues={'b': out_q})
    op.join()
    sorted_batch = out_q.pop()
    col0s = []
    for record in sorted_batch:
        col0s.append(record[0])
    ns.eq_(col0s, [777, 777, 333, 123])


def test_sort_by_string():
    in_q, out_q = (BatchQueue(), BatchQueue())
    in_q.push(_create_test_batch())
    in_q.push(None)

    op = Sort('col1', input_queues={'a': in_q}, output_queues={'b': out_q})
    op.join()
    sorted_batch = out_q.pop()
    col1s = []
    for record in sorted_batch:
        col1s.append(record[1])
    ns.eq_(col1s, ['101', '11', '200', '30'])
