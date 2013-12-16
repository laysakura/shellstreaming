# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.master
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides master process's entry point
"""
import os
from os.path import abspath, dirname, join
import shlex
import logging
from subprocess import Popen
from shellstreaming.config import Config
from shellstreaming.logger import TerminalLogger
from shellstreaming.comm.util import wait_worker_server


logger = TerminalLogger(logging.DEBUG)


def main(confpath):
    """Master process's entry point.

    :param confpath: path to config file
    :returns: exit status of master process
    """
    config = Config(confpath)

    # setup logger
    global logger
    logger = TerminalLogger(config.get('master', 'log_level'))
    logger.debug('hello from master')

    # launch worker servers (auto-deploy)
    _launch_workers(
        config.get('worker', 'hosts'), config.get('worker', 'port'),
        cnf_sent_to_worker=confpath,
    )
    return 0


def _launch_workers(worker_hosts, worker_port,
                    cnf_sent_to_worker=None,
                    parallel_deploy=False, ssh_priv_key=None):
    """Launch every worker server and return.

    :param worker_hosts: worker hosts to launch worker servers
    :type worker_hosts:  list of hostname string
    :param worker_port:  worker servers' TCP port number
    :param cnf_sent_to_worker: if not `None`, specified config file is sent to worker hosts and used by them
    :param parallel_deploy: If `True`, auto-deploy is done in parallel. Especially useful when you have
        many :param:`worker_hosts`.
        However, if you have to input anything (pass for secret key, login password, ...),
        :param:`parallel_deploy` has to be `False`.
    :param ssh_priv_key: if not `None`, specified private key is used for ssh-login to every worker host
    """
    # [todo] - make use of ssh_config (`fabric.api.env.ssh_config_path` must be True (via cmd opt?))
    global logger

    # deploy & start workers' server
    scriptpath = join(abspath(dirname(__file__)), 'auto_deploy.py')

    cmd = 'fab -f %(script)s -H %(hosts)s %(tasks)s %(parallel_deploy)s %(ssh_priv_key)s' % {
        'script'          : scriptpath,
        'hosts'           : ','.join(worker_hosts),
        'tasks'           : 'pack deploy:cnfpath=%s start_worker:worker_server_port=%d' % (
            cnf_sent_to_worker if cnf_sent_to_worker else '',
            worker_port,
        ),
        'parallel_deploy' : '-P' if parallel_deploy else '',
        'ssh_priv_key'    : '-i ' + ssh_priv_key if ssh_priv_key else '',
    }

    p        = Popen(shlex.split(cmd), env=os.environ)
    exitcode = p.wait()
    assert(exitcode == 0)

    # wait for all workers' server to start
    # [todo] - parallel wait
    for host in worker_hosts:
        wait_worker_server(host, worker_port)
        logger.debug('connected to %s:%s' % (host, worker_port))
