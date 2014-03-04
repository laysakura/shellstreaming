# -*- coding: utf-8 -*-
"""
    shellstreaming.util.comm
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides utility functions
"""
# standard modules
import rpyc
import socket
import time
import logging

# my modules


def kill_worker_server(worker_host, worker_port):
    """Try to connect to worker server, and kill it if it is.

    :raises: :class:`IOError` if unable to connect worker server.
    """
    logger = logging.getLogger('TerminalLogger')

    try:
        conn = connect_or_msg(worker_host, worker_port)
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
    logger = logging.getLogger('TerminalLogger')

    t_start = time.time()
    while True:
        # check timeout
        if timeout_sec and time.time() - t_start >= timeout_sec:
            raise IOError('timed out: cannot connect to %s:%s' % (worker_host, worker_port))

        # try connection
        try:
            conn = connect_or_msg(worker_host, worker_port)
            conn.close()
            logger.debug('connection to %s:%s is confirmed' % (worker_host, worker_port))
            return
        except (socket.gaierror, socket.error):  # connection refused
            logger.debug('waiting for %s:%s to launch ...' % (worker_host, worker_port))
            time.sleep(0.1)
            continue
        except:
            raise


def connect_or_msg(hostname, port):
    """Kinder message than rpyc.connect when failed to connect
    """
    logger = logging.getLogger('TerminalLogger')
    try:
        return rpyc.connect(hostname, port)
    except (socket.gaierror, socket.error):
        logger.warn('Connection is refused by %s:%s ...' % (hostname, port))
        raise
    except:
        logger.error('Unexpected error happened during connecting to %s:%s' % (hostname, port))
        raise


def rpyc_namespace(host_port):
    """Return rpyc's root namespace of :param:`host_port`"""
    logger = logging.getLogger('TerminalLogger')

    # [todo] - too ugly?
    import shellstreaming.worker.worker_struct as ws
    if host_port in ws.conn_pool:  # only worker has ws.conn_pool set; from worker to worker
        conn_pool = ws.conn_pool
    else:                          # from master to worker
        import shellstreaming.master.master_struct as ms
        conn_pool = ms.conn_pool
    conn = conn_pool[host_port]
    try:
        return conn.root
    except EOFError:
        logger.warn('"connection closed by peer" error when connecting to %s:%s. try re-connecting...' % (host_port))
        conn_pool[host_port] = connect_or_msg(*host_port)
        return rpyc_namespace(host_port)
