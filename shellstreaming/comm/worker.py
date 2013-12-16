# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.worker
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker process's entry point.

    .. note::
        This script is supposed to run via `python` command in worker nodes.
"""
import argparse
import sys
import shlex
import os
from os.path import abspath, dirname, join
from subprocess import Popen, STDOUT
from ConfigParser import SafeConfigParser as Config
from shellstreaming.comm.worker_server import WorkerServerService


config = Config()
config.read('/home/nakatani/git/shellstreaming/shellstreaming/test/data/shellstreaming.cnf')


def main(port, cnfpath):
    """Worker process's entry point.

    :param port: TCP port number to launch worker server
    :param cnfpath: path to config file
    :returns: exit status of worker process
    """
    _run_worker_server(port, cnfpath)

    return 0


def _run_worker_server(port, cnfpath):
    global config
    script     = join(dirname(abspath(__file__)), 'run_worker_server.py')
    deploy_dir = join(dirname(abspath(__file__)), '..', '..', '..')
    virtualenv_activator = join(deploy_dir, 'bin', 'activate')
    cmd = 'nohup sh -c ". %(virtualenv)s ; python %(script)s --config=%(cnfpath)s --port=%(port)d" &' % {
        'virtualenv' : virtualenv_activator,
        'script'     : script,
        'cnfpath'    : cnfpath,
        'port'       : port,
    }

    Popen(shlex.split(cmd), env=os.environ,
          # stderr=STDOUT, stdout=WorkerServerService.logger  # [todo] - redirect to logger
    )
    WorkerServerService.logger.debug('Start new process: "%s"'  % (cmd))


def parse_args():
    parser = argparse.ArgumentParser('shellstreaming worker entry poing')

    parser.add_argument(
        '--config', '-c',
        required=True,
        help='Configuration file')
    parser.add_argument(
        '--port', '-p',
        type=int,
        required=True,
        help='TCP port number to run server')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    sys.exit(main(port=args.port, cnfpath=args.config))
