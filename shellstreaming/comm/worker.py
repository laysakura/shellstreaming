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
from subprocess import Popen
from ConfigParser import SafeConfigParser as Config


def main(cnfpath):
    """Worker process's entry point.

    :param port: TCP port number to launch worker server
    :param cnfpath: path to config file
    :returns: exit status of worker process
    """
    config = Config()
    config.read(cnfpath)
    _run_worker_server(config.getint('worker', 'port'), cnfpath)
    return 0


def _run_worker_server(port, cnfpath):
    script     = join(dirname(abspath(__file__)), 'run_worker_server.py')
    deploy_dir = join(dirname(abspath(__file__)), '..', '..', '..')
    virtualenv_activator = join(deploy_dir, 'bin', 'activate')
    cmd = 'nohup sh -c ". %(virtualenv)s ; python %(script)s --config=%(cnfpath)s --port=%(port)d" &' % {
        'virtualenv' : virtualenv_activator,
        'script'     : script,
        'cnfpath'    : cnfpath,
        'port'       : port,
    }

    Popen(shlex.split(cmd), env=os.environ)
    print('Start new process: "%s"'  % (cmd))  # logger is only available in child process above


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
    sys.exit(main(args.config))
