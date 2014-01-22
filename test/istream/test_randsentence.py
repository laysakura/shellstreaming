# -*- coding: utf-8 -*-
import nose.tools as ns
from shellstreaming.core.batch_queue import BatchQueue
from shellstreaming.istream.randsentence import RandSentence


def test_randint_usage():
    q = BatchQueue()
    t = RandSentence(output_queue=q, max_records=100)

    # consume batches
    num_records = 0
    while True:
        batch = q.pop()
        if batch is None:  # producer has end data-fetching
            break
        for record in batch:
            num_records += 1
            # print(record)
    ns.eq_(num_records, 100)

    t.join()
