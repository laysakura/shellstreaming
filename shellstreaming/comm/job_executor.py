# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.job_executor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Abstract executor of jobs for workers
"""
import importlib

from abc import ABCMeta, abstractmethod



# JobDispatcherは，JobExecutorをexecuteするんじゃだめ．
# conn.root.JobRegisterみたいなのでworkerにjobを登録だけする．
# 各workerは，WorkerServerServiceでmasterからのリクエストを受けつつも，登録されたjobを別のスレッドで実行していく
# (JobRegisterは，jobの登録だけじゃなくて削除もできるIFにしよう．)



class JobExecutor(object):
    """Abstract executor of jobs for worker processes"""
    __metaclass__ = ABCMeta

    def __init__(self, job_id, job_class_fullname, job_args, gen_in_batches=None):
        """Creates executor of jobs

        :param job_id:    job's id
        :param job_class_fullname: job_class's name followed by full module name.
                                   :func:`importlib.import_module()` can take this string.
        :param job_args:  arguments for :param:`job_class`.__init()__
        :type job_args:  `tuple`
        :param gen_in_batches: generator object of input batches. Since inputstream does not have ascendant job,
                               it can be `None` for :class:`InputStreamExecutor`.
        """
        self._job_id = job_id

        self._job_class = getattr(
            importlib.import_module('.'.join(job_class_fullname.split('.')[:-1])),
            job_class_fullname.split('.')[-1]
        )

        self._job_args       = job_args
        self._gen_in_batches = gen_in_batches

    @abstractmethod
    def exposed_execute(self):
        """Main loop of each job"""
        pass
