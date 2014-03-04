# -*- coding: utf-8 -*-
"""
    shellstreaming.core.partitioned_batch_queue
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis:
"""
# standard modules
import threading

# 3rd party modules
import pyhashxx

# my modules
from shellstreaming.core.batch import Batch
from shellstreaming.core.batch_queue import BatchQueue


class PartitionedBatchQueue(object):
    """Queue of output batch"""

    def __init__(self, num_q, partition_key):
        """Constructor

        :param num_q: number of internal :class:`BatchQueue`.
            Number of workers is expected to be used
        :param partition_key: column name of records in batch.
            value of this column is used to distribute record to internal queues.
        """
        self._qs       = [BatchQueue() for i in range(num_q)]
        self._key      = partition_key
        self._records  = 0
        self._lock     = threading.Lock()
        self._finished = False

    def push(self, batch):
        """"""
        if batch is None:
            map(lambda i: self._qs[i].push(None), range(len(self._qs)))
            return

        self._lock.acquire()
        self._records += len(batch)
        self._lock.release()

        # [todo] - performance: splitting batch too small?
        rdef = batch.record_def()

        # distribute records using hash function
        partitioned_records = [
            []  # array of Record
            for i in range(len(self._qs))
        ]
        key_idx = rdef.colindex_by_colname(self._key)
        for rec in batch:
            val     = rec[key_idx]
            h       = pyhashxx.hashxx(bytes(val))  # [todo] - customize hash function?
            records = partitioned_records[h % len(self._qs)]
            records.append(rec)

        # really push distributed records into BatchQueue
        for i in range(len(self._qs)):
            self._qs[i].push(Batch(rdef, partitioned_records[i]))

    def pop(self, pop_from):
        """

        :param pop_from: queue id to pop batch from.
            Worker number is expected to be used.
        :type pop_from: int
        """
        q     = self._qs[pop_from]
        batch = q.pop()

        if batch is None:
            self._finished = True
            self.push(None)  # supply `None` again in case other consumers are informed `empty`
            return None

        self._lock.acquire()
        self._records -= len(batch)
        self._lock.release()

        return batch

    def records(self):
        if self._finished:
            return None
        return self._records
