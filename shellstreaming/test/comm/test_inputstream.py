from nose.tools import *
import rpyc
from multiprocessing import Process
import time
from os.path import abspath, dirname, join
from shellstreaming.config import Config
from shellstreaming.comm.inputstream import InputStreamDispatcher, InputStreamExecutorService


TEST_CONFIG   = join(abspath(dirname(__file__)), '..', 'data', 'shellstreaming.cnf')
TEST_TEXTFILE = join(abspath(dirname(__file__)), '..', 'data', 'comm_inputstream_input01.txt')


process = None


def _start_worker_thread():
    from rpyc.utils.server import ThreadPoolServer as Server
    Server(InputStreamExecutorService, port=int(Config.instance().get('worker', 'port'))).start()


def setup():
    # setting up worker
    global process
    process = Process(target=_start_worker_thread)
    process.daemon = True  # child process is killed when parent process ends
    process.start()
    # wait for worker process to really start
    while True:
        try:
            conn = rpyc.connect('localhost', int(Config.instance().get('worker', 'port')))
            conn.close()
            break
        except:  # connection refused
            time.sleep(0.1)
            continue
    print('worker server has been started')


def teardown():
    print('worker process is being killed')


def test_inputstream_dispatcher():
    # master's code
    stream = InputStreamDispatcher(
        'localhost',  # Config.instance().get('worker', 'worker1')
        'TextFile',
        (TEST_TEXTFILE, 20),
    )

    # do everything master needs to do

    stream.join()
    # TODO: need another way to close dispatched stream?
    # (maybe by adding callback to InputStreamDispatcher.__init__)
