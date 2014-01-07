# -*- coding: utf-8 -*-
import nose.tools as ns
import time
from shellstreaming.istream.stdin import Stdin


def test_stdin_usage():
    pass
    # stream = Stdin(batch_span_ms=1000)
    # for batch in stream:
    #     print('a batch contents ----')
    #     for record in batch:
    #         ns.eq_(len(record), 1)
    #         print(record)
