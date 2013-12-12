# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.master
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides master process's entry point
"""
import os
from os.path import abspath, dirname, join
import shlex
from subprocess import Popen


def main():
    """Master process's entry point.

    :returns: exit status of master process
    """
    print('hello from master')
    _launch_workers('/home/nakatani/git/shellstreaming/shellstreaming/test/data/shellstreaming_test_auto_deploy02.cnf')
    return 0


def _launch_workers(confpath):
    """
    :param confpath: path to config file
    """
    scriptpath = join(abspath(dirname(__file__)), 'auto_deploy.py')
    _env = os.environ
    _env['SHELLSTREAMING_CNF'] = confpath
    p = Popen(shlex.split('fab -f %s pack deploy' % (scriptpath)),
              env=_env)
    exitcode = p.wait()

    import sys
    sys.exit(exitcode)

    # fabでworkerのrpycサーバ立てに行く
    # 各workerについて，connectionを試みるループを回す(もちろんmasterで複数スレッドでやりたい)
    from rpyc.utils.server import ThreadedServer as Server
    server = Server(InputStreamExecutorService,
                    # port=int(config.get('master', 'port'))
    )
    server.start()
