# -*- coding: utf-8 -*-
"""
    shellstreaming.worker.job_registrar
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Registrar of jobs
"""
# standard module
import cPickle as pickle

# my module
from shellstreaming.worker import worker_struct as ws


class JobRegistrar(object):
    """"""

    def exposed_register(self, job_id):
        """Register :param:`job_id` to execute"""
        if job_id not in ws.ASSIGNED_JOBS:
            ws.ASSIGNED_JOBS.append(job_id)

    def exposed_unregister(self, job_id):
        """Unregister :param:`job_id` from job list to execute"""
        assert(job_id in ws.ASSIGNED_JOBS)
        ws.ASSIGNED_JOBS.remove(job_id)

    def exposed_finished_jobs(self):
        """Return list of might-finished jobs"""
        return pickle.dumps(ws.finished_jobs)
