# -*- coding: utf-8 -*-
"""
    shellstreaming.worker.worker_server
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker process's server
"""
# standard module
import cPickle as pickle

# 3rd party module
import rpyc

# my module
from shellstreaming.worker import worker_struct as ws
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

    def exposed_start_worker_local_scheduler(
            self,
            sched_module_name, reschedule_interval_sec, remote_queue_placement_getter
    ):
        """Start worker local scheduler"""
        return start_sched_loop(sched_module_name, reschedule_interval_sec, remote_queue_placement_getter)

    def exposed_reg_job_graph(self, pickled_job_graph):
        """Register job graph"""
        job_graph = pickle.loads(pickled_job_graph)
        ws.JOB_GRAPH = job_graph

    # APIs for workers
    def exposed_queue_netref(self, stream_edge_id):
        """Pass wrapper of BatchQueue to be remotely accessed

        :returns: `None` when this worker does not have queue corresponding to :param:`stream_edge_id`
        """
        try:
            q = ws.local_queues[stream_edge_id]
            return RemoteQueue(q)
        except KeyError:
            return None
