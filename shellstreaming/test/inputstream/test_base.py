# -*- coding: utf-8 -*-
from nose.tools import *
from shellstreaming.batch_queue import BatchQueue
from shellstreaming.inputstream.base import Base, InfiniteStream, FiniteStream


@raises(TypeError)
def test_Base_abstract_class():
    obj = Base(BatchQueue(), 1000)


@raises(TypeError)
def test_InfiniteStream_abstract_class():
    obj = InfiniteStream(BatchQueue(), 1000)


@raises(TypeError)
def test_FiniteStream_abstract_class():
    obj = FiniteStream(BatchQueue(), 1000)


def test_FiniteStream_add_no_record():
    class EmptyStream(FiniteStream):
        def __init__(self, output_queue, batch_span_ms=1000):
            FiniteStream.__init__(self, output_queue, batch_span_ms)

        def run(self):
            self.add(None)

    q = BatchQueue()
    stream = EmptyStream(q)
    assert(q.pop() is None)
