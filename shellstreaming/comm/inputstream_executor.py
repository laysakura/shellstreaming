# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.inputstream_executor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Abstract executor of jobs for workers
"""
# from shellstreaming.comm.worker_server_service import WorkerServerService
from shellstreaming.worker import worker_struct as ws
from shellstreaming.comm.job_executor import JobExecutor


class InputStreamExecutor(JobExecutor):
    """"""

    def exposed_execute(self):
        """Main loop of each job"""
        stream = self._job_class(*self._job_args)
        ws.job_instance[self._job_id] = stream
        for batch in stream:
            InputStreamExecutor._store_new_batch(batch)

    @staticmethod
    def _store_new_batch(batch):
        """Store batch into worker's memory"""
        # print('[worker] new batch is stored: %s' % (batch))
        # [todo] - put batch into worker's memory
        pass
