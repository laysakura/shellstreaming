# -*- coding: utf-8 -*-
"""
    shellstreaming.core.batch_queue
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides queue of output batch

    Simple wrapper of internal queue class
"""
import Queue as q
import threading


class BatchQueue(object):
    """Queue of output batch"""

    # [todo] - use ActiveMQ for performance?

    def __init__(self):
        """Constructor"""
        self._q        = q.Queue()
        self._records  = 0  # BatchQueue would be popped/pushed at the same time. Atomically inc/dec this var.
        self._lock     = threading.Lock()
        self._finished = False

    def push(self, batch):
        """"""
        self._q.put(batch)
        if batch is not None:
            self._lock.acquire()
            self._records += len(batch)
            self._lock.release()

    def pop(self):
        """"""
        batch = self._q.get(timeout=0.01)  # workaround: enable Ctrl-C http://bugs.python.org/issue1360
        if batch is None:
            self._finished = True
            self.push(None)  # supply `None` again in case other consumers are informed `empty`
            return None

        self._lock.acquire()
        self._records -= len(batch)
        self._lock.release()

        return batch

    def records(self):
        if self._finished:
            return None
        return self._records
