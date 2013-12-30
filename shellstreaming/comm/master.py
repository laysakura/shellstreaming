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
import networkx as nx
import shellstreaming
from shellstreaming.logger import setup_TerminalLogger
from shellstreaming.config import get_default_conf
from shellstreaming.util import import_from_file
from shellstreaming.comm.run_worker_server import start_worker_server_thread
from shellstreaming.comm.job_dispatcher import JobDispatcher
from shellstreaming.comm.util import wait_worker_server, kill_worker_server
from shellstreaming.jobgraph import JobGraph
from shellstreaming.api import *


DEFAULT_CONFIGS = (expanduser(join('~', '.shellstreaming.cnf')), )
"""Path from which default config file is searched (from left)"""


def main():
    """Master process's entry point.

    :returns: exit status of master process
    """
    # parse args
    args = _parse_args()

    # setup config
    cnfpath = args.config if args.config else _get_existing_cnf(DEFAULT_CONFIGS)
    config  = _setup_config(cnfpath)

    # setup logger
    setup_TerminalLogger(config.get('master', 'log_level'))
    logger = logging.getLogger('TerminalLogger')
    logger.info('Used config file: %s' % (cnfpath))

    # launch worker servers
    (worker_hosts, worker_port) = (config.get('worker', 'hosts').split(','), config.getint('worker', 'port'))
    if config.getboolean('debug', 'single_process_debug'):
        # launch a worker server on localhost
        logger.debug('Entering single_process_debug mode')
        t = start_worker_server_thread(worker_port, logger)
    else:
        # auto-deploy, launch worker server on worker hosts
        _launch_workers(
            worker_hosts, worker_port,
            cnf_sent_to_worker=cnfpath,
            parallel_deploy=config.getboolean('auto_deploy', 'parallel_deploy'),
            ssh_private_key=config.get('auto_deploy', 'ssh_private_key'),
            send_latest_codes_on_start=config.getboolean('auto_deploy', 'send_latest_codes_on_start'),
        )

    try:
        # make job graph from user's stream app description
        job_graph = _parse_stream_py(args.stream_py)
        if config.get('master', 'job_graph_path') != '':
            _draw_job_graph(job_graph, config.get('master', 'job_graph_path'))
        # start master's main loop
        _do_stream_processing(job_graph, worker_hosts, worker_port)
    except KeyboardInterrupt as e:
        logger.debug('Received `KeyboardInterrupt`. Killing all worker servers ...')
        for host in worker_hosts:
            kill_worker_server(host, worker_port)
        logger.exception(e)

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


def _setup_config(cnfpath):
    if cnfpath is None:
        raise IOError('Config file not found: Specify via `--config` option or put one of %s.' % (DEFAULT_CONFIGS))
    config = get_default_conf()
    config.read(cnfpath)
    return config


def _get_existing_cnf(cnf_candidates=DEFAULT_CONFIGS):
    for cnfpath in cnf_candidates:
        if os.path.exists(cnfpath):
            return cnfpath
    return None


def _launch_workers(worker_hosts, worker_port,
                    cnf_sent_to_worker,
                    parallel_deploy,
                    ssh_private_key,
                    send_latest_codes_on_start,
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
    logger = logging.getLogger('TerminalLogger')

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


def _parse_stream_py(stream_py):
    """Parse stream processing description and return job graph.

    :param stream_py: python script in which stream processings are described by users
    :returns: job graph
    :rtype:   :class:`JobGraph()`
    """
    module    = import_from_file(stream_py)
    main_func = getattr(module, 'main')
    job_graph = JobGraph()
    main_func(job_graph)
    return job_graph


def _draw_job_graph(job_graph, path):
    import matplotlib.pyplot as plt
    nx.draw(job_graph)
    plt.savefig(path)
    logger = logging.getLogger('TerminalLogger')
    logger.info('Job graph figure is generated on: %s' % (path))


def _do_stream_processing(job_graph, worker_hosts, worker_port):
    # [todo] - separate from master.py as scheduler codes

    # dispatch inputstreams
    for n in job_graph.begin_nodes():
        istream = job_graph.node[n]
        print(istream)
        stream = JobDispatcher(worker_hosts[0], worker_port, istream['name'], istream['args'])
    #     # dispatch(job, worker_hosts[0]])  # どうやってdispatchしたopをmigrateしよう?
    #     #                                  # これが実際に何をやってるかによって，実行プロファイルを得たり，それからまたdispatchを変えたりってコードが変わってくる
    stream.join()
    pass
