# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.outputstream_executor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Abstract executor of outputstream for workers
"""
from shellstreaming.worker import worker_struct as ws
from shellstreaming.comm.job_executor import JobExecutor


class OutputStreamExecutor(JobExecutor):
    """"""

    def __init__(self, job_id, job_class, job_args, gen_in_batches):
        """"""
        JobExecutor.__init__(self, job_id, job_class, job_args, gen_in_batches)

    def exposed_execute(self):
        """Main loop of each job"""
        print(self._job_class, self._job_args)
        ostream = self._job_class(*self._job_args)
        print(ostream)
        ws.job_instance[self._job_id] = ostream
        for batch in self._gen_in_batches():
            ostream.write2(batch)
