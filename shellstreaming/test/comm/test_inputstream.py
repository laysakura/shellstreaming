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
from shellstreaming.logger import TerminalLogger as Logger
from shellstreaming.comm.worker_server import WorkerServerService
from shellstreaming.comm.inputstream_dispatcher import InputStreamDispatcher
from shellstreaming.comm.util import kill_worker_server


TEST_CONFIG   = join(abspath(dirname(__file__)), '..', 'data', 'shellstreaming.cnf')
TEST_TEXTFILE = join(abspath(dirname(__file__)), '..', 'data', 'comm_inputstream_input01.txt')


process = None  # used by master process
server  = None  # used by worker process
config  = None  # used by master process


def _sigusr1_handler(signum, stack):
    # close worker server
    global server
    server.close()
    exit(0)


def _start_worker_process():
    # register SIGUSR1 handler
    # [fix] - really needs SIGUSR1? SIGHUP might be used
    import signal
    signal.signal(signal.SIGUSR1, _sigusr1_handler)

    # start worker server
    global server
    from rpyc.utils.server import ThreadedServer as Server
    config = Config(TEST_CONFIG)
    server = Server(WorkerServerService, port=int(config.get('worker', 'port')))
    server.start()


def setup():
    global process, config
    config = Config(TEST_CONFIG)
    import logging
    logger = Logger(logging.DEBUG)

    # kill worker server if exists
    try:
        kill_worker_server('localhost', 18871)  # [fix] - hardcoding
        logger.debug('Killed already-exist worker process: %s:%s' % ('localhost', 18871))
    except IOError:
        pass

    # setting up worker
    process = Process(target=_start_worker_process)
    process.start()

    # wait for worker process to really start
    while True:
        try:
            logger.debug('trying to connect localhost ...')
            conn = rpyc.connect('localhost', int(config.get('worker', 'port')))
            conn.close()
            break
        except (socket.gaierror, socket.error):  # connection refused
            time.sleep(0.1)
            continue
        except:
            raise
    logger.debug('localhost\'s server has been started')


def teardown():
    print('worker process is being killed')
    kill(process.pid, signal.SIGUSR1)


def test_inputstream_dispatcher():
    # master's code
    global config
    stream = InputStreamDispatcher(
        'localhost',
        int(config.get('worker', 'port')),
        'TextFile',
        (TEST_TEXTFILE, 20),
    )

    # do everything master needs to do

    stream.join()
    # [todo] - need another way to close dispatched stream?
    # (maybe by adding callback to InputStreamDispatcher.__init__)
