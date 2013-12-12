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
from os.path import abspath, dirname, join
from subprocess import Popen
from rpyc.utils.server import ThreadedServer as Server
from shellstreaming.logger import Logger
from shellstreaming.comm.worker_server import WorkerServerService


def main():
    """Worker process's entry point.

    :returns: exit status of worker process
    """
    logger = Logger.instance()

    # run this script as daemon
    if sys.argv[1] == 'async_start_server':
        this_script = abspath(__file__)
        deploy_dir  = join(dirname(this_script), '..', '..', '..')
        virtualenv_activator = join(deploy_dir, 'bin', 'activate')
        cmd = 'nohup sh -c ". %s ; python %s run_server" &' % (virtualenv_activator, this_script)
        Popen(shlex.split(cmd), env=os.environ)
        logger.debug('[%s async_start_server] Start new process: "%s"'  % (sys.argv[0], cmd))
    elif sys.argv[1] == 'run_server':
        start_server()
    else:  # pragma: no cover
        assert(False)

    return 0


def start_server():
    Logger.instance().debug('[%s run_server] Launching `WorkerServerService` ...' % (sys.argv[0]))
    server = Server(WorkerServerService, port=18871)
    server.start()


if __name__ == '__main__':
    assert(len(sys.argv) == 2)
    assert(sys.argv[1] in ('async_start_server', 'run_server'))
    sys.exit(main())
