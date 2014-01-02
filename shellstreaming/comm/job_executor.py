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

    def __init__(self, conn, job_id, job_class, job_args, gen_in_batches=None):
        """Creates executor of jobs

        :param conn:      connection info
        :type conn:       `(worker name, result of rpyc.connection(), connection thread)`
        :param job_id:    job's id
        :param job_class: reference to job class (one of :class:`inpustream`, :class:`outpustream`, and :class:`operator`)
        :param job_args:  arguments for :param:`job_class`.__init()__
        :type job_args:  `tuple`
        :param gen_in_batches: generator object of input batches. Since inputstream does not have ascendant job,
                               it can be `None` for :class:`InputStreamExecutor`.
        """
        self._conn           = conn
        self._job_id         = job_id
        self._job_class      = job_class
        self._job_args       = job_args
        self._gen_in_batches = gen_in_batches

    @abstractmethod
    def exposed_execute(self):
        """Main loop of each job"""
        pass
