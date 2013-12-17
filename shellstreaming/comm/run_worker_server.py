# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.run_worker_server
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: When called from shell, starts worker server.

    .. note::
        This script is supposed to be child process of `python worker.py`.

"""
import time
import sys
from threading import Thread
from rpyc.utils.server import ThreadedServer as Server
import logging
from shellstreaming.logger import FileLogger
from shellstreaming.comm.worker import parse_args
from shellstreaming.comm.worker_server import WorkerServerService


def main(port, cnfpath):
    WorkerServerService.logger = FileLogger(logging.DEBUG, '/tmp/shellstreaming.log', 1000000)  # [fix] - use config
    WorkerServerService.logger.debug('Launching `WorkerServerService` on port %d ...' % (port))

    WorkerServerService.server = Server(WorkerServerService, port=port, logger=WorkerServerService.logger)
    t = Thread(target=WorkerServerService.server.start)
    t.daemon = True
    t.start()

    while WorkerServerService.server:
        # wait for `server` to be `close()`ed by master the client.
        time.sleep(1.0)

    WorkerServerService.logger.debug('`WorkerServerService` has been closed.')
    t.join()


if __name__ == '__main__':
    args = parse_args()
    sys.exit(main(port=args.port, cnfpath=args.config))
