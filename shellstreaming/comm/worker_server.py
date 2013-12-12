# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.worker_server
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker process's server
"""
import rpyc
from shellstreaming.comm.inputstream import InputStreamExecutor


class WorkerServerService(rpyc.Service):  # pragma: no cover
                                                 # Because this class is executed by separated process,
                                                 # it's difficult to trace execution of statements inside it.
                                                 # [todo] - must be tested
    """Provides `InputStreamExecutor <shellstreaming.comm.InputStreamExecutorService.exposed_InputStreamExecutor>`_ for worker.

    .. note::
        Any class & functions in `InputStreamExecutorService` are executed by worker process.
    """
    exposed_InputStreamExecutor = InputStreamExecutor
