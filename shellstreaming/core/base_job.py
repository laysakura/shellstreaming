# -*- coding: utf-8 -*-
"""
    shellstreaming.core.base_job
    ~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides abstract base of job instances (istream, ostream, operator)
"""
import threading
from abc import ABCMeta, abstractmethod


class BaseJob(threading.Thread):
    """Base class for job instances

    job instance class must have `run()` method, which runs as a thread
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        """Runs subclasses main job (:func:`run()`)
        """
        threading.Thread.__init__(self)
        self.daemon     = True               # to die when master process dies
        self._interrupt = threading.Event()  # to become ready to die when `interrupt()` is called
        self.start()

    def interrupt(self):
        """API to safely kill thread.
        """
        self._interrupt.set()

    def _interrupted(self):
        """Function for subclasses to probe interruption"""
        return self._interrupt.is_set()

    @abstractmethod
    def run(self):  # pragma: no cover
        """Start job instance's main thread

        This function must stop after :func:`interrupt` is called
        """
        pass
