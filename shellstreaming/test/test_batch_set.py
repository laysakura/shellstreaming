# -*- coding: utf-8 -*-
from nose.tools import *
import datetime
from shellstreaming.error import UnsupportedTypeError
from shellstreaming.batch_set import BatchSet
from shellstreaming.batch import Batch
from shellstreaming.timestamp import Timestamp


def test_batch_set_usage():
    ts_start = Timestamp(datetime.datetime.now())
    ts_end   = Timestamp(datetime.datetime.now()) + 1000
    b = Batch(ts_start, ts_end)

    batches = BatchSet()
    batches.add(b)

    eq_(b,    batches.find_batch(timestamp=ts_start + 500))  # ts_start <= timestamp < ts_end
    eq_(None, batches.find_batch(timestamp=ts_end))          # timestamp >= ts_end
