# -*- coding: utf-8 -*-
from nose.tools import *
import time
from shellstreaming.batch_queue import BatchQueue
from shellstreaming.istream.randint import RandInt


def test_randint_usage():
    q       = BatchQueue()
    istream = RandInt(0, 10, q, batch_span_ms=100)
    time.sleep(1.0)  # wait for istream thread to produce batches
    istream.interrupt()    # kill istream thread

    # consume batches
    while True:
        # print('isAlive? => ', istream.isAlive())
        batch = q.pop()
        if batch is None:  # producer has end data-fetching
            break

        for i_record, record in enumerate(batch):
            ok_(0 <= record[0] <= 10)
        # print('batch has %d records' % (i_record + 1))
