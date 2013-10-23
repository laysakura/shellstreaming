# -*- coding: utf-8 -*-
from nose.tools import *
from shellstreaming.error import UnsupportedTypeError
from shellstreaming.type import Type


def test_type_usage():
    """Shows how to use Type class."""
    eq_(str(Type('STRING')), 'STRING')

    eq_(Type.equivalent_ss_type(-123), Type('INT'))


@raises(UnsupportedTypeError)
def test_unsupported_type_init():
    Type('UNSUPPORTED_TYPE')


@raises(UnsupportedTypeError)
def test_unsupported_type_equivalent():
    class X:
        pass
    Type.equivalent_ss_type(X())
