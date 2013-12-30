# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.job_executor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Abstract executor of jobs for workers
"""
from abc import ABCMeta, abstractmethod


class JobExecutor(object):
    """Abstract executor of jobs for worker processes"""
    __metaclass__ = ABCMeta

    def __init__(self, conn, job_class, job_args):
        """Creates executor of jobs

        :param conn:      connection info
        :type conn:       `(worker name, result of rpyc.connection(), connection thread)`
        :param job_class: reference to job class (one of :class:`inpustream`, :class:`outpustream`, and :class:`operator`)
        :param job_args:  arguments for :param:`job_class`.__init()__
        :type job_args:  `tuple`
        """
        self._conn      = conn
        self._job_class = job_class
        self._job_args  = job_args

    @abstractmethod
    def exposed_execute(self):
        """Main loop of each job"""
        pass
