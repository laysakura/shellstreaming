# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.worker
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker process's entry point.

    .. note::
        This script is supposed to run via `python` command in worker nodes.
"""
import sys
import shlex
import os
import time
from os.path import abspath, dirname, join
from subprocess import Popen, STDOUT
from threading import Thread
from rpyc.utils.server import ThreadedServer as Server
from shellstreaming.config import Config
from shellstreaming.comm.worker_server import WorkerServerService


config = Config('/home/nakatani/git/shellstreaming/shellstreaming/test/data/shellstreaming.cnf')


def main():
    """Worker process's entry point.

    :returns: exit status of worker process
    """
    if sys.argv[1] == 'async_start_server':
        # fork this script (on background) and call `start_server()`
        _async_start_server()
    elif sys.argv[1] == 'run_server':
        # (forked process) run server
        _run_server()
    else:  # pragma: no cover
        assert(False)

    return 0


def _async_start_server():
    global config
    this_script = abspath(__file__)
    deploy_dir  = join(dirname(this_script), '..', '..', '..')
    virtualenv_activator = join(deploy_dir, 'bin', 'activate')
    cmd = 'nohup sh -c ". %s ; python %s run_server" &' % (virtualenv_activator, this_script)

    Popen(shlex.split(cmd), env=os.environ,
          # stderr=STDOUT, stdout=WorkerServerService.logger  # [todo] - redirect to logger
    )

    WorkerServerService.logger.debug('[%s async_start_server] Start new process: "%s"'  % (sys.argv[0], cmd))


def _run_server():
    WorkerServerService.logger.debug('[%s run_server] Launching `WorkerServerService` ...' % (sys.argv[0]))

    WorkerServerService.server = Server(WorkerServerService, port=18871, logger=WorkerServerService.logger)
    t = Thread(target=WorkerServerService.server.start)
    t.start()

    while WorkerServerService.server:
        # wait for `server` to be `close()`ed by master the client.
        time.sleep(1.0)

    WorkerServerService.logger.debug('`WorkerServerService` has been closed.')
    t.join()

if __name__ == '__main__':
    assert(len(sys.argv) == 2)
    assert(sys.argv[1] in ('async_start_server', 'run_server'))
    sys.exit(main())
