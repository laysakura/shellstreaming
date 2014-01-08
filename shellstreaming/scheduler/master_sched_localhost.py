# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.master_sched_localhost
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Schedules all jobs to localhost worker (for testing purpose)
"""


def calc_job_placement(job_graph, prev_jobs_placement):
    next_jobs_placement = prev_jobs_placement.copy()
    for job_id in job_graph.nodes_iter():
        if job_id not in prev_jobs_placement:  # job is not started yet
            next_jobs_placement[job_id] = ['localhost']
    return next_jobs_placement
