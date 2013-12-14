# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.util
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides utility functions
"""
import rpyc
import socket
import time
import logging
from shellstreaming.logger import TerminalLogger


def kill_worker_server(worker_host, worker_port):
    """Try to connect to worker server, and kill it if it is.

    :raises: :class:`IOError` if unable to connect worker server.
    """
    logger = TerminalLogger(logging.DEBUG)

    try:
        conn = rpyc.connect(worker_host, worker_port)
    except (socket.gaierror, socket.error):  # connection refused
        raise IOError('%s:%s does not seem to have worker server' % (worker_host, worker_port))

    try:
        conn.root.kill()
    except EOFError:
        # Since server is closed by `WorkerServerService.exposed_kill()`,
        # "connection closed by peer" error is raised
        logger.debug('requested close worker server on %s:%s to close' % (worker_host, worker_port))


def wait_worker_server(worker_host, worker_port, timeout_sec=None):
    """Try to connect to worker server repeatedly until suceed.

    :param timeout_sec: if not `None`, raise :class:`IOError` when no connection is established after :timeout_sec:.
    :raises: :class:`IOError`
    """
    logger = TerminalLogger(logging.DEBUG)

    t_start = time.time()
    while True:
        # check timeout
        if timeout_sec and time.time() - t_start >= timeout_sec:
            raise IOError('timed out: cannot connect to %s:%s' % (worker_host, worker_port))

        # try connection
        try:
            conn = rpyc.connect(worker_host, worker_port)
            conn.close()
            logger.debug('connection to %s:%s is confirmed' % (worker_host, worker_port))
            return
        except (socket.gaierror, socket.error):  # connection refused
            time.sleep(0.5)
            continue
        except:
            raise
