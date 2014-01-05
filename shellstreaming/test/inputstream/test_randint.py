# -*- coding: utf-8 -*-
from nose.tools import *
import time
from shellstreaming.batch_queue import BatchQueue
from shellstreaming.inputstream.randint import RandInt


def test_randint_usage():
    q       = BatchQueue()
    istream = RandInt(0, 10, q, batch_span_ms=100)
    time.sleep(1.0)  # wait for istream thread to produce batches
    istream.interrupt()    # kill istream thread

    # consume batches
    while not q.empty() or istream.isAlive():
        batch = q.pop()
        for i_record, record in enumerate(batch):
            ok_(0 <= record[0] <= 10)
        # print('batch has %d records' % (i_record + 1))
