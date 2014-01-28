# -*- coding: utf-8 -*-
"""
    shellstreaming.worker.worker
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker process's entry point.

    This script only invokes :file:`run_worker_server.py` as daemon.

    .. note::
        This script is supposed to run via `python` command in worker nodes.
"""
# standard modules
import argparse
import sys
import shlex
import os
from os.path import abspath, dirname, join
from subprocess import Popen
from ConfigParser import SafeConfigParser

# my modules
from shellstreaming.config import DEFAULT_CONFIG
from shellstreaming.config.parse import parse_worker_hosts, parse_worker_path


def main(myhostname, cnfpath, logpath):
    """Worker process's entry point.

    :param myhostname: hostname of the node in which workers are being launched
    :param cnfpath: path to config file
    :param logpath: path to log file
    :returns: exit status of worker process
    """
    _run_worker_servers(myhostname, cnfpath, logpath)
    return 0


def _run_worker_servers(myhostname, cnfpath, logpath):
    script     = join(dirname(abspath(__file__)), 'run_worker_server.py')
    deploy_dir = join(dirname(abspath(__file__)), '..', '..', '..')
    virtualenv_activator = join(deploy_dir, 'bin', 'activate')
    python_egg_cache_dir = join(deploy_dir, '.python-eggs')
    os.environ['PYTHON_EGG_CACHE'] = python_egg_cache_dir

    # setup config
    config = SafeConfigParser(DEFAULT_CONFIG)
    config.read(cnfpath)

    # launch worker processes (can be multiple since one node can launch workes using different TCP ports)
    ports = _ports_of_node(myhostname,
                           config.get('shellstreaming', 'worker_hosts'),
                           config.getint('shellstreaming', 'worker_default_port'))
    for port in ports:
        cmd = 'nohup sh -c "mkdir -p %(python_egg)s ; [ -f %(virtualenv)s ] && . %(virtualenv)s ; python %(script)s --port=%(port)d --config=%(cnfpath)s >> %(logpath)s 2>&1" &' % {
            'python_egg' : python_egg_cache_dir,
            'virtualenv' : virtualenv_activator,
            'script'     : script,
            'cnfpath'    : cnfpath,
            'port'       : port,
            'logpath'    : parse_worker_path(logpath, myhostname, port),
        }
        Popen(shlex.split(cmd), env=os.environ)


def _parse_args():
    parser = argparse.ArgumentParser('shellstreaming worker entry point')

    parser.add_argument(
        '--hostname',
        required=True,
        help='Hostname of the node in which workers are being launched')
    parser.add_argument(
        '--config', '-c',
        required=True,
        help='Configuration file')
    parser.add_argument(
        '--log', '-l',
        required=True,
        help='Log file path')

    args = parser.parse_args()
    return args


def _ports_of_node(hostname, worker_hosts, default_port):
    """
    **Examples**

    .. code-block:: python
        >>> _ports_of_node('hostA', 'hostA,hostB,hostA:12345', 18871)
        [18871, 12345]
    """
    ports = []
    workers = parse_worker_hosts(worker_hosts, default_port)
    for w in workers:
        if w[0] == hostname:
            ports.append(w[1])
    return ports


if __name__ == '__main__':
    args = _parse_args()
    sys.exit(main(args.hostname, args.config, args.log))
