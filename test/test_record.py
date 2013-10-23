# -*- coding: utf-8 -*-
from nose.tools import *
from shellstreaming.record import Record
from shellstreaming.recorddef import RecordDef, RecordTypeError


def test_record_usage():
    """Shows how to use Record class."""
    rdef = RecordDef([
        {'name': 'col0',
         'type': 'STRING',
        },
        {'name': 'col1',
         # any basic type is allowed
        },
    ])
    rec = Record(
        rdef,
        'Hello', 'World'
    )
    eq_(len(rec), 2)
    rec = Record(
        rdef,
        'Hello', 777
    )
    eq_(len(rec), 2)


@raises(RecordTypeError)
def test_record_mismatch_length():
    rdef = RecordDef([
        {'name': 'col0',
         'type': 'STRING',
        },
    ])
    rec = Record(
        rdef,
        'Hello', 'World'
    )


@raises(RecordTypeError)
def test_record_mismatch_type():
    rdef = RecordDef([
        {'name': 'col0',
         'type': 'INT',
        },
    ])
    rec = Record(
        rdef,
        'not convertible to INT',
    )
