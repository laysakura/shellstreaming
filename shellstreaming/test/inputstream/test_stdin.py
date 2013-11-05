# -*- coding: utf-8 -*-
from nose.tools import *
import time
from shellstreaming.inputstream.stdin import Stdin


def test_stdin_usage():
    stream = Stdin(batch_span_ms=1000)
    for batch in stream:
        print('a batch contents ----')
        for record in batch:
            eq_(len(record), 1)
            print(record)
