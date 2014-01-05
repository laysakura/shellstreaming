# -*- coding: utf-8 -*-
"""
    shellstreaming.worker.job_registrar
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Registrar of jobs
"""
# from shellstreaming.comm.worker_server_service import WorkerServerService
from shellstreaming.worker import worker_struct as ws


class JobRegistrar(object):
    """"""

    def exposed_register(self, job_id):
        """Register :param:`job_id` to execute"""
        assert(job_id not in ws.registered_jobs)
        ws.registered_jobs.append(job_id)

    def exposed_unregister(self, job_id):
        """Unregister :param:`job_id` from job list to execute"""
        assert(job_id in ws.registered_jobs)
        del ws.registered_jobs[job_id]
