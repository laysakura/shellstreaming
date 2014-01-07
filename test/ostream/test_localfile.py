# -*- coding: utf-8 -*-
import nose.tools as ns
import os
from os.path import join
from tempfile import gettempdir
from relshell.record import Record
from relshell.recorddef import RecordDef
from relshell.batch import Batch
from shellstreaming.core.batch_queue import BatchQueue
from shellstreaming.ostream.localfile import LocalFile


TEST_FILE = join(gettempdir(), 'shellstreaming_test_localfile.txt')


def teardown():
    os.remove(TEST_FILE)


def test_localfile_usage():
    # prepare input queue
    q = BatchQueue()
    for batch in _create_batches():
        q.push(batch)    # [fix] - Batch's output format has to be customized by user
    q.push(None)

    # run ostream
    ostream = LocalFile(TEST_FILE, input_queue=q)
    ostream.join()

    # check contents
    with open(TEST_FILE) as f:
        ns.eq_(f.read(),
'''(
    ("111", )
    ("222", )
)
(
    ("333", )
)
'''
        )


def _create_batches():
    rdef = RecordDef([{'name': 'col0', 'type': 'INT'}])
    return (
        Batch(rdef, (Record(111), Record(222), )),
        Batch(rdef, (Record(333), )),
    )
