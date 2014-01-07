# -*- coding: utf-8 -*-
"""
    shellstreaming.worker.worker_server
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker process's server
"""
from threading import Thread
import cPickle as pickle
import rpyc
from shellstreaming.worker import worker_struct as ws
from shellstreaming.scheduler.worker_main import sched_loop
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
            sched_module_name, reschedule_interval_sec
    ):
        t = Thread(target=sched_loop, args=(
            ws.JOB_GRAPH, sched_module_name, reschedule_interval_sec
        ))
        t.daemon = True
        t.start()
        return t

    def exposed_reg_job_graph(self, pickled_job_graph):
        """Register job graph"""
        job_graph = pickle.loads(pickled_job_graph)
        ws.JOB_GRAPH = job_graph

    # APIs for workers
    def exposed_pop_batch(self, stream_edge_id):
        """Pass batches to caller worker from internal batch queue.

        .. note::
            This function is **blocking** just like :class:`Queue.Queue`
        """
        q     = ws.output_queues[stream_edge_id]
        batch = q.pop()
        return batch
