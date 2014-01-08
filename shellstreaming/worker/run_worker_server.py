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
from shellstreaming.util.logger import setup_TerminalLogger
from shellstreaming.util.comm import kill_worker_server
from shellstreaming.scheduler.worker_main import start_sched_loop
from shellstreaming.worker.worker_server_service import WorkerServerService


def main(cnfpath):
    # setup config
    config = SafeConfigParser(DEFAULT_CONFIG)
    config.read(cnfpath)

    # setup logger
    loglevel = eval('logging.' + config.get('shellstreaming', 'log_level'))
    setup_TerminalLogger(loglevel)
    logger = logging.getLogger('TerminalLogger')

    # start `WorkerServerService` thread
    port = config.getint('shellstreaming', 'worker_port')
    logger.debug('Launching `WorkerServerService` on port %d ...' % (port))
    th_service = start_worker_server_thread(port, logger)

    while WorkerServerService.server:    # wait for `server` to be `close()`ed by master client.
        time.sleep(1.0)

    logger.debug('`WorkerServerService` has been closed.')
    th_service.join()


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
        '--config', '-c',
        required=True,
        help='Configuration file')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = _parse_args()
    sys.exit(main(cnfpath=args.config))
