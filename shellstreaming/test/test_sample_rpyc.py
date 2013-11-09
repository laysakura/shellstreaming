import rpyc
import os
import time
from threading import Thread
from multiprocessing import Process


class FileMonitorService(rpyc.Service):
    class exposed_FileMonitor(object):   # exposing names is not limited to methods :)
        def __init__(self, filename, callback, interval = 1):
            self.filename = filename
            self.interval = interval
            self.last_stat = None
            self.callback = rpyc.async(callback)   # create an async callback
            self.active = True
            self.log = open('/tmp/worker.log', 'w')
            self.thread = Thread(target = self.work)
            self.thread.start()

        def exposed_stop(self):   # this method has to be exposed too
            self.active = False
            self.log.close()
            self.thread.join()

        def work(self):
            while self.active:
                self.log.write('working!\n')
                stat = os.stat(self.filename)
                if self.last_stat is not None and self.last_stat != stat:
                    self.callback(self.last_stat, stat)   # notify the client of the change
                self.last_stat = stat
                time.sleep(self.interval)


process = None


def _start_worker_thread():
    from rpyc.utils.server import ThreadedServer
    ThreadedServer(FileMonitorService, port=18871).start()


def setup():
    global process
    # setting up worker
    process = Process(target=_start_worker_thread)
    process.start()
    time.sleep(1)  # waiting for worker process to launch (more portable way?)


def teardown():
    global process
    process.terminate()


def test_client():
    print('hello1')

    f = open("/tmp/floop.bloop", "w")
    conn = rpyc.connect("localhost", 18871)
    bgsrv = rpyc.BgServingThread(conn)  # creates a bg thread to process incoming events

    print('hello2')

    def on_file_changed(oldstat, newstat):
        print "file changed"
        print "    old stat: %s" % (oldstat,)
        print "    new stat: %s" % (newstat,)

    mon = conn.root.FileMonitor("/tmp/floop.bloop", on_file_changed) # create a filemon

    print('hello3')

    # wait a little for the filemon to have a look at the original file
    time.sleep(1)

    f.write("shmoop") # change size
    f.flush()
    time.sleep(1)
    print('sleeping...')

    f.write("groop") # change size
    f.flush()
    time.sleep(1)
    print('sleeping...')

    f.close()

    mon.stop()
    bgsrv.stop()
    conn.close()
