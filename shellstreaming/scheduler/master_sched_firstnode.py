# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.master_sched_firstnode
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Schedules all jobs to localhost worker (for testing purpose)
"""


def calc_job_placement(job_graph, worker_hosts, prev_jobs_placement):
    next_jobs_placement = prev_jobs_placement.copy()
    for job_id in job_graph.nodes_iter():
        if not prev_jobs_placement.is_started(job_id) and not prev_jobs_placement.is_finished(job_id):
            next_jobs_placement.assign(job_id, worker_hosts[0])
    return next_jobs_placement
