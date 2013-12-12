# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.master
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides master process's entry point
"""


def main():
    """Master process's entry point.

    :returns: exit status of master process
    """
    print('hello from master')
    _launch_workers()
    return 0


def _launch_workers(confpath):
    """
    :param confpath: path to config file
    """
    

    # fabでworkerのrpycサーバ立てに行く
    # 各workerについて，connectionを試みるループを回す(もちろんmasterで複数スレッドでやりたい)
    from rpyc.utils.server import ThreadedServer as Server
    server = Server(InputStreamExecutorService,
                    # port=int(config.get('master', 'port'))
    )
    server.start()
