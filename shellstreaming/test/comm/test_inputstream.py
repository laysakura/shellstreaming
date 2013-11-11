from nose.tools import *
import rpyc
from multiprocessing import Process
import time
from os.path import abspath, dirname, join
from shellstreaming.config import config
from shellstreaming.comm.inputstream import InputStreamDispatcher, InputStreamExecutorService


TEST_FILE = join(abspath(dirname(__file__)), '..', 'data', 'comm_inputstream_input01.txt')


process = None


def _start_worker_thread():
    from rpyc.utils.server import ThreadPoolServer as Server
    Server(InputStreamExecutorService, port=int(config.get('worker', 'port'))).start()


def setup():
    # setting up worker
    global process
    process = Process(target=_start_worker_thread)
    process.start()
    # wait for worker process to really start
    while True:
        try:
            conn = rpyc.connect('localhost', int(config.get('worker', 'port')))
            conn.close()
            break
        except:  # connection refused
            time.sleep(0.1)
            continue
    print('worker server has been started')


def teardown():
    global process
    print('worker process is being killed')
    process.terminate()


def test_inputstream_dispatcher():
    # master's code
    stream = InputStreamDispatcher(
        'localhost',  # config.get('worker', 'worker1')
        'TextFile',
        (TEST_FILE, 20),
    )

    # do everything master needs to do

    stream.join()
    # TODO: need another way to close dispatched stream?
    # (maybe by adding callback to InputStreamDispatcher.__init__)
