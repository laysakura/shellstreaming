# -*- coding: utf-8 -*-
from nose.tools import *
import os
import time
from shellstreaming.inputstream.textfile import TextFile


TEST_FILE = os.path.abspath(os.path.dirname(__file__)) + '/test_textfile_input01.txt'


def test_textfile_usage():
    stream = TextFile(TEST_FILE, batch_span_ms=100)
    for batch in stream:
        if batch is None:
            time.sleep(0.1)
            continue
        for record in batch:
            eq_(len(record), 1)
            line = record[0]
            eq_('line ', line[0:5])
            ok_(0 <= int(line[5:]) < 100)  # record order in a batch is not always 'oldest-first'
