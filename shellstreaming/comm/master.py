# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.master
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides master process's entry point
"""
import os
from os.path import abspath, dirname, join
import shlex
import time
from subprocess import Popen
from shellstreaming.config import Config
from shellstreaming.logger import TerminalLogger
from shellstreaming.comm.util import kill_worker_server, wait_worker_server


# global objects referenced from master's code: `shellstreaming.comm.master.logger`
config = None
"""The config"""

logger = None
"""The logger"""


def main(confpath):
    """Master process's entry point.

    :param confpath: path to config file
    :returns: exit status of master process
    """
    _init(confpath)

    print('hello from master')

    # [todo] - もしここで18871番にconnectできたら，そのプロセスは終了しとく

    _launch_workers(confpath)
    return 0


def _init(confpath):
    """Every initialization master process has to do"""
    global logger, config

    # setup config object
    config = Config(confpath)

    # setup logger
    logger = TerminalLogger(config.get('master', 'log_level'))


def _launch_workers(cnfpath):
    """
    :param cnfpath: path to config file
    """
    global logger, config

    # deploy & start workers' server
    scriptpath = join(abspath(dirname(__file__)), 'auto_deploy.py')

    cmd = 'fab -f %(script)s -H %(hosts)s %(tasks)s' % {
        'script': scriptpath,
        'hosts': 'gueze.logos.ic.i.u-tokyo.ac.jp',
        'tasks': 'pack deploy:cnfpath=%s start_worker' % (cnfpath),
    }

    p = Popen(shlex.split(cmd), env=os.environ)
    exitcode = p.wait()
    assert(exitcode == 0)

    # wait for all workers' server to start
    wait_worker_server('gueze.logos.ic.i.u-tokyo.ac.jp', 18871)

    logger.debug('connected to gueze!!')

    time.sleep(5)

    # worker process も殺す
    kill_worker_server('gueze.logos.ic.i.u-tokyo.ac.jp', 18871)

    import sys
    sys.exit(0)

    # fabでworkerのrpycサーバ立てに行く
    # 各workerについて，connectionを試みるループを回す(もちろんmasterで複数スレッドでやりたい)
    from rpyc.utils.server import ThreadedServer as Server
    server = Server(InputStreamExecutorService,
                    # port=int(config.get('master', 'port'))
    )
    server.start()
