# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.worker_server
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker process's server
"""
import rpyc
from shellstreaming.comm.job_executor import JobExecutor


class WorkerServerService(rpyc.Service):
    """Worker process's server"""

    # `rpyc.utils.server.*Server`'s instance
    server = None

    # the logger
    logger = None

    # API to clients
    exposed_JobExecutor = JobExecutor

    def exposed_kill(self):
        WorkerServerService.server.close()
        WorkerServerService.server = None
