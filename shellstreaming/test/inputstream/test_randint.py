# -*- coding: utf-8 -*-
from nose.tools import *
from shellstreaming.inputstream.randint import RandInt


def test_randint_usage():
    n_batches = 2
    stream = RandInt(0, 10, batch_span_ms=100)
    for i_batch, batch in enumerate(stream):
        for i_record, record in enumerate(batch):
            assert_greater_equal(record[0], 0)
            assert_less_equal   (record[0], 10)
        print('batch#%d has %d records' % (i_batch, i_record + 1))

        n_batches -= 1
        if n_batches == 0:
            stream.interrupt()
