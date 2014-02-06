# -*- coding: utf-8 -*-
"""
    shellstreaming.core.remote_queue
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides wrapper of :class:`BatchQueue` to remotely poped
"""
import cPickle as pickle


class RemoteQueue(object):
    """"""

    def __init__(self, batch_queue, min_records_in_aggregated_batches):
        """
        :param batch_queue: instance of :class:`BatchQueue` or :class:`PartitionedBatchQueue` to be wrapped
        """
        self._q     = batch_queue
        self._empty = False
        # optimization: aggregated communication
        self._min_records_in_aggregated_batches = min_records_in_aggregated_batches

    def exposed_pop(self, pop_from=None):
        if self._empty:
            return None  # no batch_queue access if it already emits None

        aggr_batches = []  # optimization: aggregated transfer of batches
        num_aggr_rec = 0
        while num_aggr_rec < self._min_records_in_aggregated_batches:
            if pop_from is None:
                assert(self._q.__class__.__name__ == 'BatchQueue')
                batch = self._q.pop()
            else:
                assert(self._q.__class__.__name__ == 'PartitionedBatchQueue')
                batch = self._q.pop(pop_from)

            aggr_batches.append(batch)

            if batch is None:  # empty for the first time
                self._empty = True
                break

            num_aggr_rec += len(batch)

        return pickle.dumps(aggr_batches)

    def exposed_internal_queue_class(self):
        return self._q.__class__.__name__
