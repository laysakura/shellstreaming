# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.run_worker_server
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
from shellstreaming.logger import setup_FileLogger, setup_TerminalLogger
from shellstreaming.comm.worker_server_service import WorkerServerService


def main(cnfpath):
    # setup config
    config = SafeConfigParser(DEFAULT_CONFIG)
    config.read(cnfpath)

    # setup logger
    (loglevel, logpath) = (eval('logging.' + config.get('worker', 'log_level')), config.get('worker', 'log_path'))
    setup_FileLogger(loglevel, logpath)
    logger = logging.getLogger('FileLogger')
    setup_TerminalLogger(loglevel)
    logging.getLogger('TerminalLogger').debug('Log is written in <%s> in `%s` level' % (logpath, loglevel))

    # start `WorkerServerService` thread
    port = config.getint('worker', 'worker_port')
    logger.debug('Launching `WorkerServerService` on port %d ...' % (port))
    th_service = start_worker_server_thread(port, logger)

    # start worker-local scheduling thread
    logger.debug('Starting worker-local scheduler')
    th_sched = start_worker_local_scheduler(config.get('worker', 'worker_scheduler_module'))

    while WorkerServerService.server:    # wait for `server` to be `close()`ed by master client.
        time.sleep(1.0)

    logger.debug('`WorkerServerService` has been closed.')
    th_service.join()
    th_sched.join()


def start_worker_server_thread(port, logger):
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
