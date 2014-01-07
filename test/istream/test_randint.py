# -*- coding: utf-8 -*-
import nose.tools as ns
import time
from shellstreaming.core.batch_queue import BatchQueue
from shellstreaming.istream.randint import RandInt


def test_randint_usage():
    q       = BatchQueue()
    istream = RandInt(0, 10, output_queue=q, batch_span_ms=100)
    time.sleep(1.0)  # wait for istream thread to produce batches
    istream.interrupt()    # kill istream thread

    # consume batches
    while True:
        batch = q.pop()
        if batch is None:  # producer has end data-fetching
            break
        for i_record, record in enumerate(batch):
            ns.ok_(0 <= record[0] <= 10)
        # print('batch has %d records' % (i_record + 1))


def test_max_records():
    q       = BatchQueue()
    istream = RandInt(0, 10, output_queue=q, batch_span_ms=100, max_records=1000)

    # consume batches
    num_records = 0
    while True:
        batch = q.pop()
        if batch is None:  # producer has end data-fetching
            break
        for i_record, record in enumerate(batch):
            num_records += 1
    ns.eq_(num_records, 1000)
