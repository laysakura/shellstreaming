# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.job_dispatcher
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Dispatcher of jobs for master
"""
import rpyc


class JobDispatcher(object):
    """Asynchronous job dispatcher"""
    def __init__(self, worker, worker_port, job_id, job_class, job_args, gen_in_batches=None):
        """Create job dispatcher

        :param worker:      worker's reachable hostname or IP address
        :param worker_port: worker's `rpyc` port
        :param job_id:    job's id
        :param job_class:   reference to job class (one of :class:`inpustream`, :class:`outpustream`, and :class:`operator`)
        :param job_args:    arguments for :param:`job_class`.__init()__
        :param gen_in_batches: generator object of input batches. Since inputstream does not have ascendant job,
                               it can be `None` for :class:`InputStreamExecutor`.
        """
        self._conn      = JobDispatcher._connect(worker, worker_port)
        self._async_res = JobDispatcher._async_execute(self._conn, job_id, job_class, job_args, gen_in_batches)

    def join(self):
        """Wait for job to finish.

        After job finishes, connection to worker is closed.

        :raises: any exception raised from :func:`_async_execute`
        """
        self._async_res.wait()
        if self._async_res.error:  # pragma: no cover
            raise self._async_res.value

        (worker, connection, conn_thread) = self._conn
        conn_thread.stop()
        connection.close()

    @staticmethod
    def _connect(worker, worker_port):
        """Connect to worker"""
        connection  = rpyc.connect(worker, worker_port)  # [todo] - why not keep 1 connection per master-worker?
        conn_thread = rpyc.BgServingThread(connection)
        return (worker, connection, conn_thread)

    @staticmethod
    def _async_execute(conn, job_id, job_class, job_args, gen_in_batches):
        """Asynchronously execute job on worker process"""
        (worker, connection, conn_thread) = conn
        executor_class = JobDispatcher._get_executor_class(conn, job_class)

        # `job_class` is master's class. If passed to worker, worker has to connect to master again
        # and class instance is created on master.
        # It require's every-time communication when calling member function of `job_class`.
        # So only job_class's name is passed to worker, and worker will dynamically import job
        executor = executor_class(job_id,
                                  '.'.join([job_class.__module__, job_class.__name__]),
                                  job_args,
                                  gen_in_batches)

        # asynchronously call `JobExecutor.exposed_execute`, in which callbacks are called
        aexecute = rpyc.async(executor.execute)
        return aexecute()

    @staticmethod
    def _get_executor_class(conn, job_class):
        (worker, connection, conn_thread) = conn
        pkg_path = job_class.__module__.split('.')
        if 'inputstream' in pkg_path:
            return connection.root.InputStreamExecutor
        elif 'outputstream' in pkg_path:
            return connection.root.OutputStreamExecutor
        else:
            assert False
