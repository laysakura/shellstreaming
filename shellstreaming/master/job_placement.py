# -*- coding: utf-8 -*-
"""
    shellstreaming.master.job_placement
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: 
"""
import copy


class JobPlacement(object):
    """"""

    def __init__(self, job_graph):
        """"""
        self._job_graph  = job_graph

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

        self._fixed_job = {}
        """Some jobs (typically some ostream) are fixed to some worker.

        .. code-block:: python
            {
                '<fixed job id>': [<worker id>, ...],
                ...
            }
        """
        for job_id, job_attr in job_graph.nodes_iter(data=True):
            fixed_workers = job_attr['fixed_to']
            if fixed_workers is not None:
                self._fixed_job[job_id] = fixed_workers

    def fixed_to(self, job_id):
        """Return worker_id which :param:`job_id` is fixed to"""
        return self._fixed_job[job_id] if job_id in self._fixed_job else None

    def is_started(self, job_id):
        """Return if :param:`job_id` is already assigned to at least 1 worker"""
        return job_id in self._job_place

    def is_finished(self, job_id):
        """Return if :param:`job_id` is already finished"""
        return self.is_started(job_id) and self._job_place[job_id] == []

    def are_all_finished(self):
        for j in self._job_graph.nodes():
            if not self.is_finished(j):
                return False
        return True

    def assign(self, job_id, worker_id):
        """Assign :param:`job_id` to :param:`worker_id`

        :raises: `ValueError` when :param:`job_id` is fixed to other workers
        """
        if self.fixed_to(job_id) and worker_id not in self.fixed_to(job_id):
            raise ValueError('%s is fixed to %s' % (job_id, self.fixed_to(job_id)))
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

    def assigned_jobs(self, worker_id):
        """Return list of jobs which are are assigned to :param:`worker_id`"""
        return filter(lambda j: worker_id in self.assigned_workers(j), self._job_place.keys())

    def copy(self):
        """Returns deep copy of `self`"""
        obj = JobPlacement(self._job_graph)
        obj._job_place = copy.deepcopy(self._job_place)
        obj._fixed_job = copy.deepcopy(self._fixed_job)
        return obj

    def __str__(self):
        return str(self._job_place)
