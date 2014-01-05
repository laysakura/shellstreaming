# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.master_sched_localhost
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Schedules all jobs to localhost worker (for testing purpose)
"""


def calc_job_placement(prev_jobs_placement):
    next_jobs_placement = {}
    for job_id in prev_jobs_placement.iterkeys():
        next_jobs_placement[job_id] = ['localhost']
    return next_jobs_placement
