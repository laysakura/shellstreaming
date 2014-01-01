# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.run_worker_server
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: When called from shell, starts :class:`WorkerServerService`.

    .. note::
        This script is supposed to be child process of `python worker.py`.

"""
import argparse
import time
import sys
from os.path import join
from tempfile import gettempdir
from ConfigParser import SafeConfigParser as Config
from threading import Thread
from rpyc.utils.server import ThreadedServer as Server
import logging
from shellstreaming.logger import setup_FileLogger, setup_TerminalLogger
from shellstreaming.comm.worker_server_service import WorkerServerService


DEFAULT_CONFIG_VALUE = {
    'log_path'  : join(gettempdir(), 'shellstreaming-worker.log'),
    'log_level' : 'DEBUG',
}
"""Default key-values of config file. Keys not included in this dict is required config."""


def main(cnfpath):
    # setup config
    config = Config(DEFAULT_CONFIG_VALUE)
    config.read(cnfpath)

    # setup logger
    (loglevel, logpath) = (eval('logging.' + config.get('worker', 'log_level')), config.get('worker', 'log_path'))
    setup_FileLogger(loglevel, logpath)
    logger = logging.getLogger('FileLogger')
    setup_TerminalLogger(loglevel)
    logging.getLogger('TerminalLogger').debug('Log is written in <%s> in `%s` level' % (logpath, loglevel))

    # start `WorkerServerService`
    port = config.getint('worker', 'port')
    WorkerServerService.logger.debug('Launching `WorkerServerService` on port %d ...' % (port))
    t = start_worker_server_thread(port, logger)

    while WorkerServerService.server:
        # wait for `server` to be `close()`ed by master the client.
        time.sleep(1.0)

    logger.debug('`WorkerServerService` has been closed.')
    t.join()


def start_worker_server_thread(port, logger):
    WorkerServerService.server = Server(WorkerServerService, port=port, logger=logger)
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
