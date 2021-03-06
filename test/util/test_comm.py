# -*- coding: utf-8 -*-
import nose.tools as ns
from rpyc.utils.server import ThreadedServer as Server
from threading import Thread
from shellstreaming.worker.worker_server_service import WorkerServerService
from shellstreaming.util.comm import kill_worker_server, wait_worker_server


@IOError
def test_wait_worker_server_timeout():
    wait_worker_server('localhost', 17777, timeout_sec=1.0)  # IOError after timeout when no server is established


def test_kill_worker_server():
    port = 18888  # expected to be used only by this test

    WorkerServerService.server = Server(WorkerServerService, port=port)
    t = Thread(target=WorkerServerService.server.start)
    t.daemon = True
    t.start()

    wait_worker_server('localhost', port)
    kill_worker_server('localhost', port)


@ns.raises(IOError)
def test_kill_worker_server_when_no_server():
    kill_worker_server('localhost', 19999)  # IOError when no server is established
