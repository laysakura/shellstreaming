from nose.tools import *
import rpyc
from multiprocessing import Process
import time
import os

from importlib import import_module


class InputStreamStarterService(rpyc.Service):
    class exposed_InputStreamStarter(object):
        def __init__(self, callback, inputstream, args):
            self._callback    = callback
            self._inputstream = inputstream
            self._args        = args

        def exposed_start(self):
            module       = import_module('shellstreaming.inputstream.textfile')
            stream_class = getattr(module, self._inputstream)
            stream       = stream_class(*self._args)

            n_records = 0
            for batch in stream:
                for record in batch:
                    eq_(len(record), 1)
                    line = record[0]
                    eq_('line ', line[0:5])
                    ok_(0 <= int(line[5:]) < 100)  # record order in a batch is not always 'oldest-first'
                    n_records += 1
            self._callback(n_records)


process = None


def _start_worker_thread():
    from rpyc.utils.server import ThreadPoolServer as Server  # can be ThreadedServer or ThreadPoolServer for performance
    print('[pid=%d] strating worker server' % (os.getpid()))
    Server(InputStreamStarterService, port=18871).start()


def setup():
    global process
    # setting up worker
    print('[pid=%d] starting worker process' % (os.getpid()))
    process = Process(target=_start_worker_thread)
    process.start()
    # wait for worker process to start server
    while True:
        try:
            conn = rpyc.connect('localhost', 18871)
            conn.close()
            break
        except:  # connection refused
            time.sleep(0.1)
            continue


def teardown():
    global process
    print('[pid=%d] terminating worker process' % (os.getpid()))
    process.terminate()


bgsrv = conn = None
stop = False


def f(number_of_lines):  # masterの呼び出すcallback
    global bgsrv, conn, stop
    print '[pid=%d] finish!!! (%d lines)' % (os.getpid(), number_of_lines)


def test_jobdispatcher_makes_worker_input_file():
    global bgsrv, conn
    conn = rpyc.connect("localhost", 18871)  # conn to worker  (arg of config={'allow_pickle': True}) does not fasten execution
    bgsrv = rpyc.BgServingThread(conn)

    starter = conn.root.InputStreamStarter(
        f,
        'TextFile',
        ('/home/nakatani/git/shellstreaming/shellstreaming/test/inputstream/test_textfile_input01.txt', )
    )

    # async
    astart = rpyc.async(starter.start)
    async_res = astart()

    # do everything master want to do

    async_res.wait()
    if async_res.error:
        raise async_res.value

    bgsrv.stop()
    conn.close()
