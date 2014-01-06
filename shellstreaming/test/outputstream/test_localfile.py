# -*- coding: utf-8 -*-
from nose.tools import *
import os
from os.path import join
from tempfile import gettempdir
from relshell.record import Record
from relshell.recorddef import RecordDef
from relshell.batch import Batch
from shellstreaming.outputstream.localfile import LocalFile


TEST_FILE = join(gettempdir(), 'shellstreaming_test_localfile.txt')


def teardown():
    os.remove(TEST_FILE)


def test_localfile_usage():
    stream  = _create_batches()
    ostream = LocalFile(TEST_FILE)
    for batch in stream:
        ostream.write(batch)    # [fix] - Batch's output format has to be customized by user

    # check contents
    with open(TEST_FILE) as f:
        eq_(f.read(),
'''(
    ("col0": "111", )
    ("col0": "222", )
)
(
    ("col0": "333", )
)
'''
        )


def _create_batches():
    rdef = RecordDef([{'name': 'col0', 'type': 'INT'}])
    return (
        Batch((
            Record(rdef, 111),
            Record(rdef, 222),
        )),
        Batch((
            Record(rdef, 333),
        ))
    )
