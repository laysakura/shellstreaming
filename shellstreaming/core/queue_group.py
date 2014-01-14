# -*- coding: utf-8 -*-
"""
    shellstreaming.core.queue_group
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides wrapper of :class:`BatchQueue` and :class:`RemoteQueue`.
"""
# standard modules
import time
import random
import cPickle as pickle

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
        self._edge           = edge_id
        self._workers_to_pop = worker_ids[:]  # workers who have non-empty queue
        self._working        = False

    def pop(self):
        """Pop batch from (local|remote) queue.

        Blocks while ws.BLOCKED_BY_MASTER flag is True.
        This is for `stop the world` implementation.
        """
        import logging
        logger = logging.getLogger('TerminalLogger')

        # pop a batch, or return None when no batch is available
        while True:
            # select a queue
            if ws.WORKER_ID in self._workers_to_pop:
                # optimization: local queue first
                worker = ws.WORKER_ID
                q      = ws.local_queues[self._edge]
            else:
                worker = select_remote_worker_to_pop(self._edge, self._workers_to_pop)  # [fix] - make this function replacable
                q      = rpyc_namespace(worker).queue_netref(self._edge)
            batch = q.pop()
            if batch is not None:
                break
            # edge corresponding to this `worker` is already closed at least on selected worker
            self._workers_to_pop.remove(worker)
            if self._workers_to_pop == []:
                logger.error('[%s] finished (got None from all queues in queue group)' % (self._edge))
                break

        if type(batch) == str:
            batch = pickle.loads(batch)

        # when comming to this code path (just before returning batch, or changing state),
        # it means job instance thread is working.
        # must be blocked if master requests so.
        self._working = True
        self._block_if_necessary()
        self._working = False

        logger.error('[%s] popping batch from local queue of %s' % (self._edge, worker))
        return batch

    def is_working(self):
        """Return whether this QueueGroup is working any batch (, which means worker is not paused)"""
        return self._working

    def _block_if_necessary(self):
        while ws.BLOCKED_BY_MASTER:
            self._working = False
            time.sleep(0.001)
