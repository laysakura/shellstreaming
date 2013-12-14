# -*- coding: utf-8 -*-
from nose.tools import *
from rpyc.utils.server import ThreadedServer as Server
from threading import Thread
from shellstreaming.comm.worker_server import WorkerServerService
from shellstreaming.comm.util import kill_worker_server, wait_worker_server


def test_wait_worker_server():
    # timeoutを投げる例?
    pass


def test_kill_worker_server():
    port = 18888  # expected to be used only by this test

    WorkerServerService.server = Server(WorkerServerService, port=port)
    t = Thread(target=WorkerServerService.server.start)
    t.daemon = True
    t.start()

    wait_worker_server('localhost', port)
    kill_worker_server('localhost', port)


@raises(IOError)
def test_kill_worker_server_when_no_server():
    kill_worker_server('localhost', 19999)  # IOError when no server is established
