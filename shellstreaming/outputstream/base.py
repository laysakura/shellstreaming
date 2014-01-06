# -*- coding: utf-8 -*-
"""
    shellstreaming.outputstream.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides abstract ostream
"""
import threading
from abc import ABCMeta, abstractmethod


class Base(threading.Thread):
    """Base class for ostream

    An outputstream class must have `run()` method, which runs as a thread to write input batch to outside.
    """
    __metaclass__ = ABCMeta

    def __init__(self, input_queue):
        """Constructor

        :param input_queue:  queue to input batches
        """
        self._batch_q = input_queue

        # threading
        threading.Thread.__init__(self)
        self.daemon     = True               # to die when master process dies
        self._interrupt = threading.Event()  # to become ready to die when `interrupt()` is called
        self.start()

    def interrupt(self):
        """API to safely kill data-fetching thread.
        """
        self._interrupt.set()

    def _interrupted(self):
        """Function for outputstream subclasses to probe interruption"""
        return self._interrupt.is_set()

    @abstractmethod
    def run(self):  # pragma: no cover
        """Start ostream thread

        This function must stop after :func:`interrupt` is called
        """
        pass
