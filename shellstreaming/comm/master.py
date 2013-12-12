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
from shellstreaming.logger import Logger


def main():
    """Master process's entry point.

    :returns: exit status of master process
    """
    print('hello from master')
    _launch_workers('/home/nakatani/git/shellstreaming/shellstreaming/test/data/shellstreaming_test_auto_deploy01.cnf')
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

    # wait for all workers' server to start
    while True:
        try:
            conn = rpyc.connect('gueze.logos.ic.i.u-tokyo.ac.jp', port=18871)
            conn.close()
            break
        except (socket.gaierror, socket.error):  # connection refused
            time.sleep(10.0)  # [todo] - 0.1?
            Logger.instance().debug('waiting gueze worker server ...')
            continue
        except:
            raise

    Logger.instance().debug('connected to gueze!!')

    import sys
    sys.exit(exitcode)

    # fabでworkerのrpycサーバ立てに行く
    # 各workerについて，connectionを試みるループを回す(もちろんmasterで複数スレッドでやりたい)
    from rpyc.utils.server import ThreadedServer as Server
    server = Server(InputStreamExecutorService,
                    # port=int(config.get('master', 'port'))
    )
    server.start()
