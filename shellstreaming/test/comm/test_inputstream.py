# -*- coding: utf-8 -*-
from nose.tools import *
import rpyc
from multiprocessing import Process
import time
import signal
from os import kill
from os.path import abspath, dirname, join
import socket
from shellstreaming.config import Config
from shellstreaming.comm.inputstream import InputStreamDispatcher, WorkerServerService


TEST_CONFIG   = join(abspath(dirname(__file__)), '..', 'data', 'shellstreaming.cnf')
TEST_TEXTFILE = join(abspath(dirname(__file__)), '..', 'data', 'comm_inputstream_input01.txt')


process = None  # used by master process
server  = None  # used by worker process


def _sigusr1_handler(signum, stack):
    # close worker server
    global server
    server.close()
    exit(0)


def _start_worker_process():
    # register SIGUSR1 handler
    import signal
    signal.signal(signal.SIGUSR1, _sigusr1_handler)

    # start worker server
    global server
    from rpyc.utils.server import ThreadedServer as Server
    config = Config.instance()
    config.set_config_file(TEST_CONFIG)
    server = Server(WorkerServerService, port=int(config.get('worker', 'port')))
    server.start()


def setup():
    # setting up worker
    global process
    process = Process(target=_start_worker_process)
    process.start()
    # wait for worker process to really start
    config = Config.instance()
    config.set_config_file(TEST_CONFIG)
    while True:
        try:
            conn = rpyc.connect(config.get('worker_list', 'worker0'), int(config.get('worker', 'port')))
            conn.close()
            break
        except (socket.gaierror, socket.error):  # connection refused
            time.sleep(0.1)
            continue
        except:
            raise
    print('worker server has been started')


def teardown():
    print('worker process is being killed')
    kill(process.pid, signal.SIGUSR1)


def test_inputstream_dispatcher():
    # master's code
    stream = InputStreamDispatcher(
        Config.instance().get('worker_list', 'worker0'),
        'TextFile',
        (TEST_TEXTFILE, 20),
    )

    # do everything master needs to do

    stream.join()
    # [todo] - need another way to close dispatched stream?
    # (maybe by adding callback to InputStreamDispatcher.__init__)
