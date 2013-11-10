from nose.tools import *
import rpyc
from multiprocessing import Process
import time

from shellstreaming.inputstream.textfile import TextFile


class InputStreamStarterService(rpyc.Service):
    class exposed_InputStreamStarter(object):
        def __init__(self, callback, inputstream, args):
            module = __import__('shellstreaming.inputstream.textfile', globals(), locals(), [inputstream], -1)
            stream = eval('%s %s' % (inputstream, args))

            n_records = 0
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
    conn = rpyc.connect("localhost", 18871)  # conn to worker  (arg of config={'allow_pickle': True}) does not fasten execution
    # もしかしたら，確実にサーバ側(worker側)の方のTextFileクラスを読ませるためにeval的なのが必要かも．
    # eval('os.path')は成功した
    bgsrv = rpyc.BgServingThread(conn)

    obj = conn.root.InputStreamStarter(
        f,
        'TextFile',
        ('/home/nakatani/git/shellstreaming/shellstreaming/test/inputstream/test_textfile_input01.txt', )
    )

    print('can do everything here!!')
    time.sleep(3)

    bgsrv.stop()
    conn.close()
