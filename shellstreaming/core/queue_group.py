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

    def __init__(self, edge_id, worker_ids, min_records_in_aggregated_batches):
        """
        :param edge_id: edge corresponding to this QueueGroup
        :param worker_ids: workers who have `param`:edge_id:'s queue
        """
        self._edge             = edge_id
        self._workers_to_pop   = worker_ids[:]  # workers who have non-empty queue
        self._batch_local_repo = deque()        # cache aggregated batches locally
        self._min_records_in_aggregated_batches = min_records_in_aggregated_batches  # optimization: batch aggregation

    def pop(self):
        """Pop batch from (local|remote) queue.
        """
        # pop a batch, or return None when no batch is available
        while True:

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
                select_func = ws.IN_QUEUE_SELECTION_MODULE.select_remote_worker_to_pop
                from_worker = select_func(self._edge, self._workers_to_pop)
                if from_worker == ws.WORKER_ID:  # from local queue
                    q       = ws.local_queues[self._edge]
                    q_class = q.__class__.__name__
                else:
                    q       = rpyc_namespace(from_worker).queue_netref(self._edge, self._min_records_in_aggregated_batches)
                    q_class = q.internal_queue_class()
                    self._last_remote_worker = from_worker

                # pop batch from BatchQueue or PartitionedBatchQueue
                # if selected queue is Empty at that time, retry pop
                try:
                    if q_class == 'BatchQueue':
                        batch = q.pop()
                    elif q_class == 'PartitionedBatchQueue':
                        batch = q.pop(pop_from=ws.WORKER_NUM_DICT[ws.WORKER_ID])  # [fix] - partition_key を指定された下流ジョブが fixed_to で部分ワーカ集合を指定していた場合，グローバルなワーカ番号を使うと，例えば3つのキューのキュー#1は使われないのにキュー#4を要求されたり大変なことになる
                    else:
                        assert(False)
                    break
                except:  # queue was empty
                    pass # retry

            # batch from remote queue
            if type(batch) == str:
                batches = pickle.loads(batch)  # batch from remote queue is aggregated
                for b in batches:              # cache locally
                    self._batch_local_repo.append(b)
                batch = self._batch_local_repo.popleft()

            if batch is None:
                # edge corresponding to this `worker` is already closed at least on selected worker
                self._workers_to_pop.remove(from_worker)
                continue

            assert(batch is not None)
            return batch
