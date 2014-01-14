# -*- coding: utf-8 -*-
"""
    shellstreaming.core.batch_queue
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides queue of output batch

    Simple wrapper of internal queue class
"""
import Queue as q


class BatchQueue(object):
    """Queue of output batch"""

    # [todo] - use ActiveMQ for performance?

    def __init__(self):
        """Constructor"""
        self._q = q.Queue()

    def push(self, batch):
        """"""
        self._q.put(batch)

    def pop(self):
        """"""
        batch = self._q.get(timeout=365 * 24 * 60 * 60)  # workaround: enable Ctrl-C http://bugs.python.org/issue1360
        if batch is None:
            self.push(None)  # supply `None` again in case other consumers are informed `empty`
        return batch

    def empty(self):
        """"""
        return self._q.qsize() == 0
