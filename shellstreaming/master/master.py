# -*- coding: utf-8 -*-
"""
    shellstreaming.master.master
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides master process's entry point
"""
# standard module
import argparse
import os
from os.path import abspath, dirname, join
import shlex
import logging
from subprocess import Popen
from ConfigParser import SafeConfigParser

# 3rd party
import cPickle as pickle
import networkx as nx
import rpyc

# my module
from shellstreaming.config import DEFAULT_CONFIG, DEFAULT_CONFIG_LOCATION
from shellstreaming.util.logger import setup_TerminalLogger
from shellstreaming.util.importer import import_from_file
from shellstreaming.worker.run_worker_server import start_worker_server_thread
from shellstreaming.scheduler.master_main import sched_loop
from shellstreaming.util.comm import wait_worker_server, kill_worker_server
import shellstreaming.master.master_struct as ms
from shellstreaming import api


def main():
    """Master process's entry point.

    :returns: exit status of master process
    """
    # parse args
    args = _parse_args()

    # setup config
    cnfpath = args.config if args.config else _get_existing_cnf(DEFAULT_CONFIG_LOCATION)
    config  = _setup_config(cnfpath)

    # setup logger
    setup_TerminalLogger(config.get('shellstreaming', 'log_level'))
    logger = logging.getLogger('TerminalLogger')
    logger.info('Used config file: %s' % (cnfpath))

    # overwrite worker_hosts when localhost_debug
    if config.getboolean('shellstreaming', 'localhost_debug'):
        config.set('shellstreaming', 'worker_hosts', 'localhost')

    # launch worker servers
    worker_hosts = config.get('shellstreaming', 'worker_hosts').split(',')
    worker_port  = config.getint('shellstreaming', 'worker_port')
    if config.getboolean('shellstreaming', 'localhost_debug'):
        # launch a worker server on localhost
        logger.debug('Entering localhost_debug mode')
        th_service = start_worker_server_thread(worker_port, logger)
    else:
        # auto-deploy, launch worker server on worker hosts
        _launch_workers(
            worker_hosts, worker_port,
            cnf_sent_to_worker=cnfpath,
            worker_log_path=config.get('shellstreaming', 'worker_log_path'),
            parallel_deploy=config.getboolean('shellstreaming', 'parallel_deploy'),
            ssh_private_key=config.get('shellstreaming', 'ssh_private_key'),
            send_latest_codes_on_start=config.getboolean('shellstreaming', 'send_latest_codes_on_start'),
        )

    try:
        # make job graph from user's stream app description
        job_graph = _parse_stream_py(args.stream_py)
        # draw job graph
        if config.get('shellstreaming', 'job_graph_path') != '':
            _draw_job_graph(job_graph, config.get('shellstreaming', 'job_graph_path'))
        # initialize :module:`master_struct`
        for host in worker_hosts:
            ms.conn_pool[host] = rpyc.connect(host, worker_port)
        # register job graph to each worker
        pickled_job_graph = pickle.dumps(job_graph)
        for host in worker_hosts:
            conn = ms.conn_pool[host]
            conn.root.reg_job_graph(pickled_job_graph)
        # launch worker-local scheduler on each worker
        for host in worker_hosts:
            conn = ms.conn_pool[host]
            conn.root.start_worker_local_scheduler(
                config.get('shellstreaming', 'worker_scheduler_module'),
                config.getint('shellstreaming', 'worker_reschedule_interval_sec'))
        # start master's main loop
        sched_loop(
            job_graph, worker_hosts, worker_port,
            config.get('shellstreaming', 'master_scheduler_module'),
            config.getint('shellstreaming', 'master_reschedule_interval_sec'))
        # run user's validation codes
        _run_test(args.stream_py)
    except KeyboardInterrupt as e:
        logger.debug('Received `KeyboardInterrupt`. Killing all worker servers ...')
        for host in worker_hosts:
            kill_worker_server(host, worker_port)
        logger.exception(e)

    return 0


def _parse_args():
    from shellstreaming import __description__
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument(
        '--config', '-c',
        default=None,
        help='''Configuration file. If not specified, %(default_configs)s are searched (from left) and one found is used.''' % {
            'default_configs': ', '.join(DEFAULT_CONFIG_LOCATION),
        })
    parser.add_argument(
        'stream_py',
        help='''Python script describing stream processings. Must have `.py` as suffix''',
    )

    args = parser.parse_args()
    return args


def _setup_config(cnfpath):
    if cnfpath is None:
        raise IOError('Config file not found: Specify via `--config` option or put one of %s.' % (DEFAULT_CONFIG_LOCATION))
    config = SafeConfigParser(DEFAULT_CONFIG)
    config.read(cnfpath)
    return config


def _get_existing_cnf(cnf_candidates=DEFAULT_CONFIG_LOCATION):
    for cnfpath in cnf_candidates:
        if os.path.exists(cnfpath):
            return cnfpath
    return None


def _launch_workers(worker_hosts, worker_port,
                    cnf_sent_to_worker,
                    worker_log_path,
                    parallel_deploy,
                    ssh_private_key,
                    send_latest_codes_on_start,
    ):
    """Launch every worker server and return.

    :param worker_hosts: worker hosts to launch worker servers
    :type worker_hosts:  list of hostname string
    :param worker_port:  worker servers' TCP port number
    :param worker_log_path: worker servers' log path
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
    scriptpath = join(abspath(dirname(__file__)), '..', 'autodeploy', 'auto_deploy.py')

    fab_tasks = []
    if send_latest_codes_on_start:
        fab_tasks.append('pack')
        fab_tasks.append('deploy:cnfpath=%s' % (cnf_sent_to_worker))
    fab_tasks.append('start_worker:cnfpath=%s,logpath=%s' % (cnf_sent_to_worker, worker_log_path))

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
    main_func()    # `api._job_graph` is changed internally
    return api._job_graph


def _run_test(stream_py):
    """Run validation code in user's script"""
    logger    = logging.getLogger('TerminalLogger')
    module    = import_from_file(stream_py)
    test_func = getattr(module, 'test', None)
    if test_func is None:
        return

    test_func_name = '%s.%s' % (test_func.__module__, test_func.__name__)
    try:
        test_func()
        logger.info('%s finished without any exception' % (test_func_name))
    except:
        logger.error('Exception has been raised in %s' % (test_func_name))
        raise


def _draw_job_graph(job_graph, path):
    import matplotlib.pyplot as plt

    pos = nx.spring_layout(job_graph)
    nx.draw(job_graph, pos)
    # red color for istream
    nx.draw_networkx_nodes(job_graph, pos, nodelist=job_graph.begin_nodes(), node_color='r')
    # blue color for ostream
    nx.draw_networkx_nodes(job_graph, pos, nodelist=job_graph.end_nodes(), node_color='b')
    # white color for operator
    nx.draw_networkx_nodes(
        job_graph, pos,
        nodelist=tuple(set(job_graph.nodes()) - set(job_graph.begin_nodes()) - set(job_graph.end_nodes())),
        node_color='w')
    # edge label
    nx.draw_networkx_edge_labels(job_graph, pos, job_graph.edge_labels)
    plt.savefig(path)

    logger = logging.getLogger('TerminalLogger')
    logger.info('Job graph figure is generated on: %s' % (path))
