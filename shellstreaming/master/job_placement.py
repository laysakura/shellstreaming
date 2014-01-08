# -*- coding: utf-8 -*-
"""
    shellstreaming.master.job_placement
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: 
"""


class JobPlacement(object):
    """"""

    def __init__(self, job_graph):
        """"""
        self._job_place = {}
        """
        .. code-block:: python
            {
                '<job id>': [<worker id>, <worker id>, ...],  # running job
                '<job id>': [],                               # finished job
                ...
            }
            # <job id> not in jobs_placement => job not started yet
        """
        self._job_graph  = job_graph

        self._fixed_jobs = []
        """Some jobs (typically some ostream) are fixed to some worker.

        .. code-block:: python
            ['<job id>', ...]
        """
        for job_id, job_attr in job_graph.nodes_iter(data=True):
            if job_attr['fixed_worker'] is not None:
                self._fixed_jobs.append(job_id)
                self._job_place[job_id] = [job_attr['fixed_worker']]

    def is_fixed(self, job_id):
        """Return wheter :param:`job_id` is fixed job"""
        return job_id in self._fixed_jobs

    def is_started(self, job_id):
        """Return if :param:`job_id` is already assigned to at least 1 worker"""
        return job_id in self._job_place

    def is_finished(self, job_id):
        """Return if :param:`job_id` is already finished"""
        return self.is_started(job_id) and self._job_place[job_id] == []

    def assign(self, job_id, worker_id):
        """Assign :param:`job_id` to :param:`worker_id`

        :raises: `ValueError` when :param:`job_id` is fixed job
        """
        if self.is_fixed(job_id):
            raise ValueError('%s is fixed to %s' % (job_id, self._job_place[job_id][0]))
        assert(worker_id not in self.assigned_workers(job_id))
        if self.is_started(job_id):
            self._job_place[job_id].append(worker_id)
        else:
            self._job_place[job_id] = [worker_id]

    def fire(self, job_id, worker_id):
        """Stop :param:`worker_id` from running :param:`job_id`"""
        if worker_id in self._job_place[job_id]:
            self._job_place[job_id].remove(worker_id)

    def assigned_workers(self, job_id):
        """Return list of workers who are assigned :param:`job_id`"""
        if not self.is_started(job_id):
            return []
        return self._job_place[job_id]

    def copy(self):
        """Returns deep copy of `self`"""
        obj = JobPlacement(self._job_graph)
        obj._job_place  = self._job_place.copy()
        obj._fixed_jobs = self._fixed_jobs[:]
        return obj

    def __str__(self):
        return str(self._job_place)
