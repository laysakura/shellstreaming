# -*- coding: utf-8 -*-
from nose.tools import *
import datetime
from shellstreaming.error import UnsupportedTypeError
from shellstreaming.timestamp import Timestamp


def test_timestamp_ops():
    ts = Timestamp(datetime.datetime.now())
    assert_less         (ts, ts + 1)
    assert_less_equal   (ts, ts)
    assert_greater      (ts, ts - 1)
    assert_greater_equal(ts, ts)
    assert_equal        (ts, ts)
    assert_not_equal    (ts, ts + 1)


def test_timestamp___int__():
    ts = Timestamp(datetime.datetime(1999, 7, 1))
    eq_(int(ts), int("1999" + "07" + "01" + "00" + "00" + "00" + "000000"))
