# -*- coding: utf-8 -*-
from nose.tools import *
import time
from os.path import abspath, dirname, join
from shellstreaming.batch_queue import BatchQueue
from shellstreaming.inputstream.textfile import TextFile


TEST_FILE = join(abspath(dirname(__file__)), '..', 'data', 'inputstream_textfile_input01.txt')


def test_textfile_usage():
    n_batches = n_records = 0

    q       = BatchQueue()
    istream = TextFile(TEST_FILE, q, batch_span_ms=20)

    # consume batches
    while True:
        batch = q.pop()
        if batch is None:  # producer has end data-fetching
            break

        n_batches += 1
        for record in batch:
            eq_(len(record), 1)
            line = record[0]
            eq_('line ', line[0:5])
            ok_(0 <= int(line[5:]) < 100)  # record order in a batch is not always 'oldest-first'
            n_records += 1

    print('number of batches (%d) >= 1 ?' % (n_batches))
    ok_(n_batches >= 1)
    eq_(n_records, 100)
