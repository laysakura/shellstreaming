# -*- coding: utf-8 -*-
from nose.tools import *
import datetime
from shellstreaming.error import RecordTypeError
from shellstreaming.record import Record
from shellstreaming.recorddef import RecordDef
from shellstreaming.timestamp import Timestamp


def test_record_usage():
    """Shows how to use Record class."""
    rdef = RecordDef([
        {'name': 'col0', 'type': 'STRING'},
        {'name': 'col1'},      # any basic type is allowed
    ])

    # col1 accepts any type
    rec = Record(rdef, 'Hello', 'World')
    eq_(len(rec), 2)
    rec = Record(rdef, 'Hello', 777)
    eq_(len(rec), 2)

    # get column by index
    eq_(rec[0], 'Hello')

    # iterate all columns
    cols = []
    for col in rec:
        cols.append(col)
    eq_(cols, ['Hello', 777])


@raises(RecordTypeError)
def test_record_mismatch_length():
    rdef = RecordDef([{'name': 'col0', 'type': 'STRING'}])
    rec  = Record(rdef, 'Hello', 'World')


@raises(RecordTypeError)
def test_record_mismatch_type():
    rdef = RecordDef([{'name': 'col0', 'type': 'INT'}])
    rec  = Record(rdef, 'not convertible to INT')


@raises(RecordTypeError)
def test_record_non_basic_type():
    class C:
        pass
    c = C  # c has too complex type as stream record

    rdef = RecordDef([{'name': 'col0'}])
    rec  = Record(rdef, c)


def test_record_user_defined_timestamp():
    rdef = RecordDef([{'name': 'col0'}])
    rec  = Record(rdef, 'hello', timestamp=Timestamp(datetime.datetime(1999, 7, 1)))
    eq_(rec.timestamp, Timestamp(datetime.datetime(1999, 7, 1)))
