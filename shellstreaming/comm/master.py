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
import socket
import rpyc
from subprocess import Popen
from shellstreaming.config import Config
from shellstreaming.logger import TerminalLogger
from shellstreaming.comm.util import kill_worker_server


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


def _launch_workers(confpath):
    """
    :param confpath: path to config file
    """
    global logger, config

    # deploy & start workers' server
    scriptpath = join(abspath(dirname(__file__)), 'auto_deploy.py')
    _env = os.environ
    _env['SHELLSTREAMING_CNF'] = confpath
    p = Popen(shlex.split('fab -f %s pack deploy start_worker' % (scriptpath)),
              env=_env)
    exitcode = p.wait()
    assert(exitcode == 0)

    # wait for all workers' server to start
    while True:
        try:
            conn = rpyc.connect('gueze.logos.ic.i.u-tokyo.ac.jp', port=18871)
            conn.close()
            break
        except (socket.gaierror, socket.error):  # connection refused
            time.sleep(0.1)
            logger.debug('waiting gueze worker server ...')
            continue
        except:
            raise

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
