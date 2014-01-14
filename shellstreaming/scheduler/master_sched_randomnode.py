# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.master_sched_firstnode
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Schedules jobs to random workers (for testing purpose)
"""
import random


def calc_job_placement(job_graph, worker_hosts, prev_jobs_placement):
    next_jobs_placement = prev_jobs_placement.copy()
    for job_id in job_graph.nodes_iter():
        # start not started & finished job
        if not prev_jobs_placement.is_started(job_id) and not prev_jobs_placement.is_finished(job_id):
            # fixed job
            fixed_workers = prev_jobs_placement.fixed_to(job_id)
            if fixed_workers is not None:
                map(lambda w: next_jobs_placement.assign(job_id, w), fixed_workers)
                continue
            # normal job
            i = random.randint(0, len(worker_hosts) - 1)
            next_jobs_placement.assign(job_id, worker_hosts[i])
    return next_jobs_placement
