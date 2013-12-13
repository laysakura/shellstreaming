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
from shellstreaming.logger import TerminalLogger


import logging
logger = TerminalLogger(logging.DEBUG)  # [todo] - use config


def main():
    """Master process's entry point.

    :returns: exit status of master process
    """
    print('hello from master')

    # [todo] - もしここで18871番にconnectできたら，そのプロセスは終了しとく

    _launch_workers('/home/nakatani/git/shellstreaming/shellstreaming/test/data/shellstreaming.cnf')
    return 0


def _launch_workers(confpath):
    """
    :param confpath: path to config file
    """
    # deploy & start workers' server
    scriptpath = join(abspath(dirname(__file__)), 'auto_deploy.py')
    _env = os.environ
    _env['SHELLSTREAMING_CNF'] = confpath
    p = Popen(shlex.split('fab -f %s pack deploy start_worker' % (scriptpath)),
              env=_env)
    exitcode = p.wait()
    assert(exitcode == 0)

    global logger

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
    new_conn = rpyc.connect('gueze.logos.ic.i.u-tokyo.ac.jp', port=18871)
    try:
        new_conn.root.kill()
    except EOFError:
        # Since server is closed by `WorkerServerService.exposed_kill()`,
        # "connection closed by peer" error is raised
        logger.debug('master has closed connection to gueze')  # [todo] - hardcoding

    import sys
    sys.exit(0)

    # fabでworkerのrpycサーバ立てに行く
    # 各workerについて，connectionを試みるループを回す(もちろんmasterで複数スレッドでやりたい)
    from rpyc.utils.server import ThreadedServer as Server
    server = Server(InputStreamExecutorService,
                    # port=int(config.get('master', 'port'))
    )
    server.start()
