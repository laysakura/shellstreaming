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

    # This fails if __ge__ is not implemented, although I expected __ne__ & __lt__ are enough
    assert_greater_equal(Timestamp(datetime.datetime(2013, 10, 31, 18, 18, 48, 492000)),
                         Timestamp(datetime.datetime(2013, 10, 31, 18, 18, 48, 488000)))


def test_timestamp___long__():
    ts = Timestamp(datetime.datetime(1999, 7, 1))
    eq_(long(ts), long("1999" + "07" + "01" + "00" + "00" + "00" + "000"))


def test_timestamp_large_number():
    ts1 = Timestamp(datetime.datetime(1999, 7, 1))
    ts2 = Timestamp(datetime.datetime(2999, 7, 1))
    assert_greater(ts2, ts1)
