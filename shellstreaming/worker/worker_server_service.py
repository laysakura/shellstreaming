# -*- coding: utf-8 -*-
"""
    shellstreaming.worker.worker_server
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker process's server
"""
# standard module
import cPickle as pickle
import time

# 3rd party module
import rpyc

# my module
from shellstreaming.worker import worker_struct as ws
from shellstreaming.core.batch_queue import BatchQueue
from shellstreaming.core.remote_queue import RemoteQueue
from shellstreaming.scheduler.worker_main import start_sched_loop
from shellstreaming.worker.job_registrar import JobRegistrar


class WorkerServerService(rpyc.Service):
    """Worker process's server"""

    # `rpyc.utils.server.*Server`'s instance
    server = None

    # APIs for master
    exposed_JobRegistrar = JobRegistrar

    def exposed_kill(self):
        """Kill worker server"""
        WorkerServerService.server.close()
        WorkerServerService.server = None

    def exposed_update_queue_groups(self, pickled_queue_groups):
        """Updates ws.QUEUE_GROUPS"""
        ws.QUEUE_GROUPS = pickle.loads(pickled_queue_groups)

    def exposed_start_worker_local_scheduler(
            self,
            sched_module_name, reschedule_interval_sec
    ):
        """Start worker local scheduler"""
        return start_sched_loop(sched_module_name, reschedule_interval_sec)

    def exposed_set_worker_id(self, worker_id):
        """Set worker_id from master"""
        ws.WORKER_ID = worker_id

    def exposed_reg_job_graph(self, pickled_job_graph):
        """Register job graph"""
        job_graph = pickle.loads(pickled_job_graph)
        ws.JOB_GRAPH = job_graph

    def exposed_block(self):
        """Master blocks worker's activity by calling this function.

        This function itself is blocking function (confusing!) in that
        it returns after worker has really stopped.
        """
        ws.BLOCKED_BY_MASTER = True
        while not ws.ack_blocked:
            time.sleep(0.001)

    def exposed_unblock(self):
        """Master restarts worker's activity by calling this function.
        """
        ws.BLOCKED_BY_MASTER = False

    def exposed_create_local_queues_if_not_exist(self, edge_ids):
        """Create local queues corresponding to :param:`edge_ids` if it is not yet created"""
        import logging
        logger = logging.getLogger('TerminalLogger')
        for e in edge_ids:
            if e not in ws.local_queues.keys():
                ws.local_queues[e] = BatchQueue()
                logger.debug('Local queue for %s is created' % (e))

    # APIs for workers
    def exposed_queue_netref(self, stream_edge_id):
        """Pass wrapper of BatchQueue to be remotely accessed
        """
        q = ws.local_queues[stream_edge_id]
        return RemoteQueue(q)
