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
