# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.worker_server
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker process's server
"""
import rpyc
from shellstreaming.comm.inputstream_executor import InputStreamExecutor
from shellstreaming.comm.outputstream_executor import OutputStreamExecutor


class WorkerServerService(rpyc.Service):
    """Worker process's server"""

    # `rpyc.utils.server.*Server`'s instance
    server = None

    # APIs for master
    exposed_InputStreamExecutor  = InputStreamExecutor
    exposed_OutputStreamExecutor = OutputStreamExecutor

    def exposed_kill(self):
        """Kill worker server"""
        WorkerServerService.server.close()
        WorkerServerService.server = None

    # APIs for workers
    def exposed_get_out_batches(num_batches=0):
        """Pass batches to caller worker from internal batch queue.

        .. note::
            This function is **blocking** just like :class:`Queue.Queue`
        """
        pass
