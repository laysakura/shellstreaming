# -*- coding: utf-8 -*-
from nose.tools import *
from shellstreaming.recorddef import RecordDef, RecordDefError
from shellstreaming.type import Type


def test_recorddef_usage():
    """Shows how to use RecordDef class."""
    rdef = RecordDef([
        {'name': 'col0',
         'type': 'STRING',
        },
        {'name': 'col1',
        },
    ])
    eq_(len(rdef), 2)
    eq_(rdef[0].name, 'col0')
    eq_(rdef[0].type, Type('STRING'))


@raises(RecordDefError)
def test_recorddef_required_key_lacks():
    rdef = RecordDef([
        {
        },  # at least 'name' is required
    ])
