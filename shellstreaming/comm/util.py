# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.util
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides utility functions
"""
import rpyc
import socket
import logging
from shellstreaming.logger import TerminalLogger


def kill_worker_server(worker_host, worker_port):
    """Try to connect to worker server, and kill it if it is.
    """
    logger = TerminalLogger(logging.DEBUG)

    try:
        conn = rpyc.connect(worker_host, worker_port)
    except (socket.gaierror, socket.error):  # connection refused
        logger.debug('%s:%s does not seem to have worker server' % (worker_host, worker_port))
        return

    try:
        conn.root.kill()
    except EOFError:
        # Since server is closed by `WorkerServerService.exposed_kill()`,
        # "connection closed by peer" error is raised
        logger.debug('closed connection to %s' % (worker_host))
        return

    assert(False)
