# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.master
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides master process's entry point
"""
import argparse
import os
from os.path import abspath, dirname, join, expanduser
import shlex
import logging
from subprocess import Popen
from ConfigParser import SafeConfigParser as Config
import shellstreaming
from shellstreaming.util import import_from_file
from shellstreaming.logger import TerminalLogger
from shellstreaming.comm.util import wait_worker_server
from shellstreaming.api import *


DEFAULT_CONFIGS = (expanduser(join('~', '.shellstreaming.cnf')), )
"""Path from which default config file is searched (from left)"""

# default arguments to _launch_workers
CNF_SENT_TO_WORKER = None
PARALLEL_DEPLOY    = False
SSH_PRIVATE_KEY    = None
SEND_LATEST_CODES_ON_START = True


logger = None


def main():
    """Master process's entry point.

    :returns: exit status of master process
    """
    # parse args
    args = _parse_args()

    # setup config
    cnfpath = args.config if args.config else _get_existing_cnf(DEFAULT_CONFIGS)
    if cnfpath is None:
        raise IOError('Config file not found: Specify via `--config` option or put one of %s.' % (DEFAULT_CONFIGS))
    config = Config()
    config.read(cnfpath)

    # setup logger
    global logger
    logger = TerminalLogger(config.get('master', 'log_level'))
    logger.info('Used config file: %s' % (cnfpath))

    # launch worker servers (auto-deploy)
    _launch_workers(
        config.get('worker', 'hosts').split(','), config.getint('worker', 'port'),
        cnf_sent_to_worker=cnfpath,
        parallel_deploy=config.getboolean('auto_deploy', 'parallel_deploy') if config.has_option('auto_deploy', 'parallel_deploy') else PARALLEL_DEPLOY,
        ssh_private_key=config.get('auto_deploy', 'ssh_private_key') if config.has_option('auto_deploy', 'ssh_private_key') else SSH_PRIVATE_KEY,
        send_latest_codes_on_start=config.getboolean('auto_deploy', 'send_latest_codes_on_start') if config.has_option('auto_deploy', 'send_latest_codes_on_start') else SEND_LATEST_CODES_ON_START,
    )

    # start main stream processing
    _start_main(args.stream_py)

    # necessary to remove error message:
    #     Exception TypeError: "'NoneType' object is not callable" in <function _removeHandlerRef at 0x7fb2b038ee60> ignored
    logger = None

    return 0


def _parse_args():
    parser = argparse.ArgumentParser(description=shellstreaming.__description__)

    parser.add_argument(
        '--config', '-c',
        default=None,
        help='''Configuration file. If not specified, %(default_configs)s are searched (from left) and one found is used.''' % {
            'default_configs': ', '.join(DEFAULT_CONFIGS),
        })
    parser.add_argument(
        'stream_py',
        help='''Python script describing stream processings. Must have `.py` as suffix''',
    )

    args = parser.parse_args()
    return args


def _get_existing_cnf(cnf_candidates=DEFAULT_CONFIGS):
    global logger
    for cnfpath in cnf_candidates:
        if os.path.exists(cnfpath):
            return cnfpath
    return None


def _launch_workers(worker_hosts, worker_port,
                    cnf_sent_to_worker=CNF_SENT_TO_WORKER,
                    parallel_deploy=PARALLEL_DEPLOY,
                    ssh_private_key=SSH_PRIVATE_KEY,
                    send_latest_codes_on_start=SEND_LATEST_CODES_ON_START,
    ):
    """Launch every worker server and return.

    :param worker_hosts: worker hosts to launch worker servers
    :type worker_hosts:  list of hostname string
    :param worker_port:  worker servers' TCP port number
    :param cnf_sent_to_worker: if not `None`, specified config file is sent to worker hosts and used by them
    :param parallel_deploy: If `True`, auto-deploy is done in parallel. Especially useful when you have
        many :param:`worker_hosts`.
        However, if you have to input anything (pass for secret key, login password, ...),
        :param:`parallel_deploy` has to be `False`.
    :param ssh_private_key: if not `None`, specified private key is used for ssh-login to every worker host
    """
    # [todo] - make use of ssh_config (`fabric.api.env.ssh_config_path` must be True (via cmd opt?))
    global logger

    # deploy & start workers' server
    scriptpath = join(abspath(dirname(__file__)), 'auto_deploy.py')

    fab_tasks = []
    if send_latest_codes_on_start:
        fab_tasks.append('pack')
        fab_tasks.append('deploy:cnfpath=%s' % (cnf_sent_to_worker))
    fab_tasks.append('start_worker:cnfpath=%s' % (cnf_sent_to_worker))

    cmd = 'fab -f %(script)s -H %(hosts)s %(tasks)s %(parallel_deploy)s %(ssh_priv_key)s' % {
        'script'          : scriptpath,
        'hosts'           : ','.join(worker_hosts),
        'tasks'           : ' '.join(fab_tasks),
        'parallel_deploy' : '-P' if parallel_deploy else '',
        'ssh_priv_key'    : '-i ' + ssh_private_key if ssh_private_key else '',
    }
    logger.debug('Auto-deploy starts with this command:%s%s' % (os.linesep, cmd))

    p        = Popen(shlex.split(cmd), env=os.environ)
    exitcode = p.wait()
    assert(exitcode == 0)

    # wait for all workers' server to start
    # [todo] - parallel wait
    for host in worker_hosts:
        wait_worker_server(host, worker_port)
        logger.debug('connected to %s:%s' % (host, worker_port))


def _start_main(stream_py):
    """Parse and execute stream processings.

    :param stream_py: python script in which stream processings are described by users
    """
    module    = import_from_file(stream_py)
    main_func = getattr(module, 'main')
    main_func()
