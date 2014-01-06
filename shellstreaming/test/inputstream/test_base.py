# -*- coding: utf-8 -*-
from nose.tools import *
from shellstreaming.batch_queue import BatchQueue
from shellstreaming.inputstream.base import Base


def test_Base_add_no_record():
    class EmptyStream(Base):
        def __init__(self, output_queue, batch_span_ms=1000):
            Base.__init__(self, output_queue, batch_span_ms)

        def run(self):
            self.add(None)

    q = BatchQueue()
    istream = EmptyStream(q)
    assert(q.pop() is None)
