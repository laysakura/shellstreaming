# -*- coding: utf-8 -*-
from nose.tools import *
import datetime
from shellstreaming.core.timespan import Timespan
from shellstreaming.core.timestamp import Timestamp


def test_timestamp_ops():
    ts = Timestamp(datetime.datetime.now())
    ok_(ts <  ts + 1)
    ok_(ts <= ts)
    ok_(ts >  ts - 1)
    ok_(ts >= ts)
    assert_equal(ts, ts)
    assert_not_equal(ts, ts + 1)

    # This fails if __ge__ is not implemented, although I expected __ne__ & __lt__ are enough
    ok_(Timestamp(datetime.datetime(2013, 10, 31, 18, 18, 48, 492000)) >=
        Timestamp(datetime.datetime(2013, 10, 31, 18, 18, 48, 488000)))


def test_timestamp___long__():
    ts = Timestamp(datetime.datetime(1999, 7, 1))
    eq_(long(ts), long("1999" + "07" + "01" + "00" + "00" + "00" + "000"))


def test_timestamp_large_number():
    ts1 = Timestamp(datetime.datetime(1999, 7, 1))
    ts2 = Timestamp(datetime.datetime(2999, 7, 1))
    ok_(ts2 > ts1)


def test_timestamp_timespan_ops():
    t = Timestamp(datetime.datetime(1999, 7, 1))
    tspan1 = Timespan(t - 1, 2)
    tspan2 = Timespan(t - 1, 1)
    tspan3 = Timespan(t + 1, 1)

    ok_(t.between(tspan1))
    ok_(t.between(tspan2))
    ok_(not t.between(tspan3))

    ok_(not t.runoff_lower(tspan1))
    ok_(not t.runoff_lower(tspan2))
    ok_(t.runoff_lower(tspan3))

    ok_(not t.runoff_higher(tspan1))
    ok_(not t.runoff_higher(tspan2))
    ok_(not t.runoff_higher(tspan3))
