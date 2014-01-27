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
            # fixed job
            fixed_workers = prev_jobs_placement.fixed_to(job_id)
            if fixed_workers is not None:
                map(lambda w: next_jobs_placement.assign(job_id, w), fixed_workers)  # 必ずfixed_toの全部にassignするのは，PartitionedBatchQueueを上流に持つジョブを終了させるために必要
                continue
            # normal job
            map(lambda w: next_jobs_placement.assign(job_id, w), worker_hosts)
    return next_jobs_placement
