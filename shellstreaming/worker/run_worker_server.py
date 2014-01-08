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
from shellstreaming.util.logger import setup_FileLogger, setup_TerminalLogger
from shellstreaming.scheduler.worker_main import start_sched_loop
from shellstreaming.worker.worker_server_service import WorkerServerService


def main(cnfpath):
    # setup config
    config = SafeConfigParser(DEFAULT_CONFIG)
    config.read(cnfpath)

    # setup logger
    loglevel = eval('logging.' + config.get('shellstreaming', 'log_level'))
    logpath  = config.get('shellstreaming', 'worker_log_path')
    setup_FileLogger(loglevel, logpath)
    logger = logging.getLogger('FileLogger')
    setup_TerminalLogger(loglevel)
    logging.getLogger('TerminalLogger').debug('Log is written in <%s> in `%s` level' % (logpath, loglevel))

    # start `WorkerServerService` thread
    port = config.getint('shellstreaming', 'worker_port')
    logger.debug('Launching `WorkerServerService` on port %d ...' % (port))
    th_service = start_worker_server_thread(port, logger)

    # start worker-local scheduling thread
    logger.debug('Starting worker-local scheduler')
    th_sched = start_sched_loop(config.get('shellstreaming', 'worker_scheduler_module'),
                                config.get('shellstreaming', 'worker_reschedule_interval_sec'))

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
