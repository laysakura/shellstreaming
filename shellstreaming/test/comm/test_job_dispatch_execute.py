# -*- coding: utf-8 -*-
from nose.tools import *
import rpyc
from multiprocessing import Process
import time
import signal
import logging
from os import kill
from os.path import abspath, dirname, join
import socket
from shellstreaming.logger import setup_TerminalLogger
from shellstreaming.batch_queue import BatchQueue
from shellstreaming.inputstream.textfile import TextFile
from shellstreaming.comm.worker_server_service import WorkerServerService
from shellstreaming.comm.job_dispatcher import JobDispatcher
from shellstreaming.comm.util import kill_worker_server


WORKER_HOST   = 'localhost'
WORKER_PORT   = 18889
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
    signal.signal(signal.SIGUSR1, _sigusr1_handler)

    # start worker server
    global server
    from rpyc.utils.server import ThreadedServer as Server
    server = Server(WorkerServerService, port=WORKER_PORT)
    server.start()


def setup():
    setup_TerminalLogger(logging.DEBUG)
    logger = logging.getLogger('TerminalLogger')

    global process
    # kill worker server if exists
    try:
        kill_worker_server(WORKER_HOST, WORKER_PORT)
        logger.debug('Killed already-exist worker process: %s:%s' % (WORKER_HOST, WORKER_PORT))
    except IOError:
        pass

    # setting up worker
    process = Process(target=_start_worker_process)
    process.start()

    # wait for worker process to really start
    while True:
        try:
            logger.debug('trying to connect %s:%s ...' % (WORKER_HOST, WORKER_PORT))
            conn = rpyc.connect(WORKER_HOST, WORKER_PORT)
            conn.close()
            break
        except (socket.gaierror, socket.error):  # connection refused
            time.sleep(0.1)
            continue
        except:
            raise
    logger.debug('%s:%s\'s worker server has been started' % (WORKER_HOST, WORKER_PORT))


def teardown():
    logger = logging.getLogger('TerminalLogger')
    logger.debug('worker process is being killed')
    kill(process.pid, signal.SIGUSR1)


def test_inputstream_dispatcher():
    # master's code
    q = BatchQueue()
    istream = JobDispatcher(
        WORKER_HOST, WORKER_PORT,
        'job_id',  # job_id is in job graph,, irrelavant to this test
        TextFile,
        (TEST_TEXTFILE, 20),
    )

    # do everything master needs to do

    istream.join()
    # [todo] - need another way to close dispatched stream?
    # (maybe by adding callback to JobDispatcher.__init__)
