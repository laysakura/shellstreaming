# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.job_executor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Executor of jobs for workers
"""


class JobExecutor(object):
    """Executor of jobs for worker processes"""
    def __init__(self, conn, job_class, job_args):
        """Creates executor of jobs

        :param conn:      connection info
        :type conn:       `(worker name, result of rpyc.connection(), connection thread)`
        :param job_class: reference to job class (one of :class:`inpustream`, :class:`outpustream`, and :class:`operator`)
        :param job_args:  arguments for :param:`job_class`.__init()__
        :type job_args:  `tuple`
        """
        self._conn             = conn
        self._job_class = job_class
        self._job_args  = job_args

    def exposed_execute(self):
        """Start inputsream.

        This function is supposed to be called by master process.
        """
        stream = JobExecutor._create_stream(self._job_class, self._job_args)
        for batch in stream:
            JobExecutor._store_new_batch(batch)

    @staticmethod
    def _create_stream(job_class, job_args):
        """Create stream object"""
        stream = job_class(*job_args)
        return stream

    @staticmethod
    def _store_new_batch(batch):
        """Store batch into worker's memory"""
        # print('[worker] new batch is stored: %s' % (batch))
        # [todo] - put batch into worker's memory
        pass
