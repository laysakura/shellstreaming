# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.worker_server
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker process's server
"""
import rpyc
import logging
from shellstreaming.logger import FileLogger
from shellstreaming.comm.inputstream_executor import InputStreamExecutor


class WorkerServerService(rpyc.Service):
    """Worker process's server"""

    # `rpyc.utils.server.*Server`'s instance
    server = None

    # the logger
    logger = FileLogger(logging.DEBUG, '/tmp/shellstreaming.log')  # [fix] - use config

    # API to clients
    exposed_InputStreamExecutor = InputStreamExecutor

    def exposed_kill(self):
        WorkerServerService.server.close()
        WorkerServerService.server = None
