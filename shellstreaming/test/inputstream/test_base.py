# -*- coding: utf-8 -*-
from nose.tools import *
from shellstreaming.inputstream.base import Base, InfiniteStream, FiniteStream


@raises(TypeError)
def test_Base_abstract_class():
    obj = Base(1000)


@raises(TypeError)
def test_InfiniteStream_abstract_class():
    obj = InfiniteStream(1000)


@raises(TypeError)
def test_FiniteStream_abstract_class():
    obj = FiniteStream(1000)


def test_FiniteStream_add_no_record():
    class EmptyStream(FiniteStream):
        def __init__(self, batch_span_ms=1000):
            FiniteStream.__init__(self, batch_span_ms)

        def run(self):
            self.add(None)

    stream = EmptyStream()
    for batch in stream:
        assert(False)
