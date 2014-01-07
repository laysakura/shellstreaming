# -*- coding: utf-8 -*-
"""
    shellstreaming.worker.worker
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker process's entry point.

    This script only invokes :file:`run_worker_server.py` as daemon.

    .. note::
        This script is supposed to run via `python` command in worker nodes.
"""
import argparse
import sys
import shlex
import os
from os.path import abspath, dirname, join
from subprocess import Popen


def main(cnfpath):
    """Worker process's entry point.

    :param cnfpath: path to config file
    :returns: exit status of worker process
    """
    _run_worker_server(cnfpath)
    return 0


def _run_worker_server(cnfpath):
    script     = join(dirname(abspath(__file__)), 'run_worker_server.py')
    deploy_dir = join(dirname(abspath(__file__)), '..', '..', '..')
    virtualenv_activator = join(deploy_dir, 'bin', 'activate')
    cmd = 'nohup sh -c "[ -f %(virtualenv)s ] && . %(virtualenv)s ; python %(script)s --config=%(cnfpath)s" &' % {
        'virtualenv' : virtualenv_activator,
        'script'     : script,
        'cnfpath'    : cnfpath,
    }
    Popen(shlex.split(cmd), env=os.environ)

    sys.stderr.write('Start new process: "%s"%s'  % (cmd, os.linesep))  # logger is not available here


def _parse_args():
    parser = argparse.ArgumentParser('shellstreaming worker entry point')

    parser.add_argument(
        '--config', '-c',
        required=True,
        help='Configuration file')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = _parse_args()
    sys.exit(main(args.config))
