# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.worker_server
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker process's server
"""
import rpyc
from shellstreaming.comm.inputstream_executor import InputStreamExecutor


class WorkerServerService(rpyc.Service):
    """Worker process's server"""
    exposed_InputStreamExecutor = InputStreamExecutor
