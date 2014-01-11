# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.master_sched_firstnode
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Schedules all jobs to first worker in list (for testing purpose)
"""


def calc_job_placement(job_graph, worker_hosts, prev_jobs_placement):
    next_jobs_placement = prev_jobs_placement.copy()
    for job_id in job_graph.nodes_iter():
        # start not started & finished job
        if not prev_jobs_placement.is_started(job_id) and not prev_jobs_placement.is_finished(job_id):
            fixed_worker = prev_jobs_placement.fixed_to(job_id)
            if fixed_worker:  # fixed job
                next_jobs_placement.assign(job_id, fixed_worker)
            else:             # normal job
                next_jobs_placement.assign(job_id, worker_hosts[0])
    return next_jobs_placement
