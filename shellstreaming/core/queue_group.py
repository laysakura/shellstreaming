# -*- coding: utf-8 -*-
"""
    shellstreaming.core.queue_group
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides wrapper of :class:`BatchQueue` and :class:`RemoteQueue`.
"""
# standard modules
import cPickle as pickle
from collections import deque

# my modules
import shellstreaming.worker.worker_struct as ws
from shellstreaming.scheduler.worker_select_queue_random import select_remote_worker_to_pop
from shellstreaming.util.comm import rpyc_namespace


class QueueGroup(object):
    """A queue group corresponds to an edge in job graph.
    Since a job is shared and executed by multiple nodes (say N nodes), the number of :class:`BatchQueue` generated
    is N (if the job has 1 output).

    QueueGroup transparently wrap up these N local queues.

    When queue placement changes, create new instance of :class:`QueueGroup`.
    """

    def __init__(self, edge_id, worker_ids):
        """
        :param edge_id: edge corresponding to this QueueGroup
        :param worker_ids: workers who have `param`:edge_id:'s queue
        """
        self._edge             = edge_id
        self._workers_to_pop   = worker_ids[:]  # workers who have non-empty queue
        self._batch_local_repo = deque()        # cache aggregated batches locally

    def pop(self):
        """Pop batch from (local|remote) queue.

        Blocks while ws.BLOCKED_BY_MASTER flag is True.
        This is for `stop the world` implementation.

        :param pop_from: worker name used for popping from :class:`PartitionedBatchQueue`.
            None is allowed when popping from :class:`BatchQueue`
        """
        # pop a batch, or return None when no batch is available
        while True:
            # only when every candidate worker returns None, this queue returns None
            if self._workers_to_pop == []:
                return None

            # return batch from aggregated batch local cache if exists
            if len(self._batch_local_repo) > 0:
                batch = self._batch_local_repo.popleft()
                if batch is None:
                    self._workers_to_pop.remove(self._last_remote_worker)
                    continue
                else:
                    return batch

            # select a queue
            if ws.WORKER_ID in self._workers_to_pop:
                # optimization: local queue first
                worker  = ws.WORKER_ID
                q       = ws.local_queues[self._edge]
                q_class = q.__class__.__name__
            else:
                worker  = select_remote_worker_to_pop(self._edge, self._workers_to_pop)  # [fix] - make this function replacable
                q       = rpyc_namespace(worker).queue_netref(self._edge)
                q_class = q.internal_queue_class()
                self._last_remote_worker = worker

            # pop batch from BatchQueue or PartitionedBatchQueue
            if q_class == 'BatchQueue':
                batch = q.pop()
            elif q_class == 'PartitionedBatchQueue':
                batch = q.pop(pop_from=ws.WORKER_NUM_DICT[ws.WORKER_ID])
            else:
                assert(False)

            if batch is None:
                # edge corresponding to this `worker` is already closed at least on selected worker
                self._workers_to_pop.remove(worker)
                continue
            else:
                break

        # after `break`
        if type(batch) == str:
            batches = pickle.loads(batch)  # batch from remote queue is aggregated
            for b in batches:              # cache locally
                self._batch_local_repo.append(b)
            batch = self._batch_local_repo.popleft()

        return batch
