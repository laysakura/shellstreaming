from nose.tools import *
import rpyc
from multiprocessing import Process
import time
from shellstreaming.config import config
from shellstreaming.comm.inputstream import InputStreamDispatcher, InputStreamExecutorService


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
        'localhost',
        'TextFile',
        ('/home/nakatani/git/shellstreaming/shellstreaming/test/inputstream/test_textfile_input01.txt', 20),
    )

    # do everything master needs to do

    stream.join()
