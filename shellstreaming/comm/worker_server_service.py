# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.worker_server
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker process's server
"""
import rpyc
from shellstreaming.worker import worker_struct as ws
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

    def exposed_reg_job_graph(self, job_graph):
        """Register job graph"""
        ws.JOB_GRAPH = job_graph

    # APIs for workers
    def exposed_get_out_batch(self, job_id):    # [todo] - better to fetch multiple batches at a time for performance?
        """Pass batches to caller worker from internal batch queue.

        .. note::
            This function is **blocking** just like :class:`Queue.Queue`

        :param job_id: job's id who outputs demanded batches
        """
        op = ws.job_instance[job_id]  # instance of inputstream or operator
        batch = op.next()
        return batch
