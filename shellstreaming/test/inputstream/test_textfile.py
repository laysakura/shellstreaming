# -*- coding: utf-8 -*-
from nose.tools import *
import time
from os.path import abspath, dirname, join
from shellstreaming.inputstream.textfile import TextFile


TEST_FILE = join(abspath(dirname(__file__)), 'test_textfile_input01.txt')


def test_textfile_usage():
    n_batches = n_records = 0
    stream = TextFile(TEST_FILE, batch_span_ms=20)
    for batch in stream:
        n_batches += 1
        for record in batch:
            eq_(len(record), 1)
            line = record[0]
            eq_('line ', line[0:5])
            ok_(0 <= int(line[5:]) < 100)  # record order in a batch is not always 'oldest-first'
            n_records += 1
    print('number of batches (%d) >= 1 ?' % (n_batches))
    assert_greater_equal(n_batches, 1)
    eq_(n_records, 100)


def test_textfile_interrupt():
    n_batches = 0
    stream = TextFile(TEST_FILE, batch_span_ms=20)
    for batch in stream:
        n_batches += 1
        stream.interrupt()
    eq_(n_batches, 1)
