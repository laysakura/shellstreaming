# -*- coding: utf-8 -*-
"""
    shellstreaming.worker.run_worker_server
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: When called from shell, starts :class:`WorkerServerService`.

    .. note::
        This script is supposed to be child process of `python worker.py`.

"""
# standard module
import argparse
import time
import sys
from threading import Thread
import logging
from ConfigParser import SafeConfigParser

# 3rd party module
from rpyc.utils.server import ThreadedServer as Server

# my module
from shellstreaming.config import DEFAULT_CONFIG
from shellstreaming.config.parse import parse_worker_hosts
from shellstreaming.util.logger import setup_TerminalLogger
from shellstreaming.util.comm import kill_worker_server, wait_worker_server, connect_or_msg
import shellstreaming.worker.worker_struct as ws
from shellstreaming.worker.worker_server_service import WorkerServerService


def main(port, cnfpath):
    # setup config
    config = SafeConfigParser(DEFAULT_CONFIG)
    config.read(cnfpath)

    # setup logger
    loglevel = eval('logging.' + config.get('shellstreaming', 'log_level'))
    setup_TerminalLogger(loglevel)
    logger = logging.getLogger('TerminalLogger')

    # start `WorkerServerService` thread
    logger.debug('Launching `WorkerServerService` on port %d ...' % (port))
    th_service = start_worker_server_thread(port, logger)

    # make connection to other workers
    workers = parse_worker_hosts(config.get('shellstreaming', 'worker_hosts'),
                                 config.getint('shellstreaming', 'worker_default_port'))
    for worker in workers:
        while True:
            try:
                wait_worker_server(*worker, timeout_sec=0.001)
                ws.conn_pool[worker] = connect_or_msg(*worker)
                break
            except IOError:
                if WorkerServerService.server is None:  # master has killed me
                    return 1

    # wait for `server` to be `close()`ed by master client.
    while WorkerServerService.server:
        time.sleep(1.0)

    logger.debug('`WorkerServerService` has been closed.')
    th_service.join()

    return 0


def start_worker_server_thread(port, logger):
    # attempt to kill already launched server (for avoiding `Address already in use`)
    try:
        kill_worker_server('localhost', port)
    except IOError:
        pass

    # start new worker server
    WorkerServerService.server = Server(
        WorkerServerService, port=port,
        logger=logger,
    )
    t = Thread(target=WorkerServerService.server.start)
    t.daemon = True
    t.start()
    return t


def _parse_args():
    parser = argparse.ArgumentParser('shellstreaming `WorkerServerService` launcher')

    parser.add_argument(
        '--port',
        required=True, type=int,
        help='TCP port number to launch this worker')
    parser.add_argument(
        '--config', '-c',
        required=True,
        help='Configuration file')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = _parse_args()
    sys.exit(main(args.port, args.config))
