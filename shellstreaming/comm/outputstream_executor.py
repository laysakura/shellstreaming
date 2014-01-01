# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.outputstream_executor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Abstract executor of outputstream for workers
"""
from shellstreaming.comm.job_executor import JobExecutor


class OutputStreamExecutor(JobExecutor):
    """"""

    def exposed_execute(self):
        """Main loop of each job"""
        ostream = self._job_class(*self._job_args)
        # [todo] - ココらへんで，前のjobからbatchを得てwriteするコードを書く
