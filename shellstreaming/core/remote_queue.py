# -*- coding: utf-8 -*-
"""
    shellstreaming.core.remote_queue
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides wrapper of :class:`BatchQueue` to remotely poped
"""
import cPickle as pickle


class RemoteQueue(object):
    """"""

    def __init__(self, batch_queue):
        """
        :param batch_queue: instance of :class:`BatchQueue` to be wrapped
        """
        self._q     = batch_queue
        self._empty = False

    def exposed_pop(self):
        if self._empty:
            return None  # no batch_queue access if it already emits None

        batch = self._q.pop()

        if batch is None:  # empty for the first time
            self._empty = True
            return None
        return pickle.dumps(batch)
