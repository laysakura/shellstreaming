# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.master_sched_allnode
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Schedules jobs to all workers, regardless of its ability to parallelize
"""
import logging


def calc_job_placement(job_graph, worker_hosts, prev_jobs_placement):
    logger = logging.getLogger('TerminalLogger')

    next_jobs_placement = prev_jobs_placement.copy()
    for job_id in job_graph.nodes_iter():
        # start not started & finished job
        if not prev_jobs_placement.is_started(job_id) and not prev_jobs_placement.is_finished(job_id):
            fixed_worker = prev_jobs_placement.fixed_to(job_id)
            if fixed_worker:  # fixed job
                next_jobs_placement.assign(job_id, fixed_worker)
            else:             # normal job
                if job_graph.node[job_id]['type'] == 'istream':
                    next_jobs_placement.assign(job_id, worker_hosts[0])
                else:
                    map(lambda w: next_jobs_placement.assign(job_id, w), worker_hosts)
    return next_jobs_placement
