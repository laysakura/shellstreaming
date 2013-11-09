from nose.tools import *
import rpyc
from multiprocessing import Process
import time

from shellstreaming.inputstream.textfile import TextFile


class InputStreamStarterService(rpyc.Service):
    class exposed_InputStreamStarter(object):
        def __init__(self, callback, inputstream):
            n_records = 0
            # stream = inputstream(args)
            print('/home/nakatani/git/shellstreaming/shellstreaming/test/inputstream/test_textfile_input01.txt')
            stream = TextFile('/home/nakatani/git/shellstreaming/shellstreaming/test/inputstream/test_textfile_input01.txt')
            for batch in stream:
                for record in batch:
                    eq_(len(record), 1)
                    line = record[0]
                    eq_('line ', line[0:5])
                    ok_(0 <= int(line[5:]) < 100)  # record order in a batch is not always 'oldest-first'
                    n_records += 1
            callback(n_records)


process = None


def _start_worker_thread():
    from rpyc.utils.server import ThreadedServer as Server  # can be ThreadedServer or ThreadPoolServer for performance
    print('strating worker server')
    Server(InputStreamStarterService, port=18871).start()


def setup():
    global process
    # setting up worker
    process = Process(target=_start_worker_thread)
    process.start()
    time.sleep(1)


def teardown():
    global process
    process.terminate()


bgsrv = conn = None


def f(number_of_lines):
    global bgsrv, conn
    print 'finish!!! (%d lines)' % (number_of_lines)


def test_jobdispatcher_makes_worker_input_file():
    global bgsrv, conn
    conn = rpyc.connect("localhost", 18871)  # conn to worker
    bgsrv = rpyc.BgServingThread(conn)

    obj = conn.root.InputStreamStarter(
        f,
        'hoge',
    )
    # obj = conn.root.InputStreamStarter(
    #     f,
    #     shellstreaming.inputstream.textfile.TextFile,
    #     ('/home/nakatani/git/shellstreaming/shellstreaming/test/inputstream/test_textfile_input01.txt', ),
    # )

    print('can do everything here!!')
    time.sleep(3)

    bgsrv.stop()
    conn.close()
