# -*- coding: utf-8 -*-
import nose.tools as ns
from os.path import abspath, dirname, join
from shellstreaming.core.batch_queue import BatchQueue
from shellstreaming.istream.textfile_tail import TextFileTail


TEST_FILE = join(abspath(dirname(__file__)), '..', 'data', 'istream_textfile_input01.txt')


# def test_textfile_tail_usage():
#     ### this test finishes after executing `$ echo a >> /tmp/a.txt` 5 times

#     q         = BatchQueue()
#     istream   = TextFileTail('/tmp/a.txt', max_records=5, output_queue=q)
#     istream.join()

#     # consume batches
#     while True:
#         batch = q.pop()
#         if batch is None:  # producer has end data-fetching
#             break


def test_textfile_tail_same_as_textfile():
    n_records = 0
    q         = BatchQueue()
    istream   = TextFileTail(TEST_FILE, read_existing_lines=True, max_records=100, output_queue=q)
    istream.join()

    # consume batches
    while True:
        batch = q.pop()
        if batch is None:  # producer has end data-fetching
            break

        for record in batch:
            ns.eq_(len(record), 1)
            line = record[0]
            ns.eq_('line ', line[0:5])
            ns.ok_(0 <= int(line[5:]) < 100)
            n_records += 1

    ns.eq_(n_records, 100)
