# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.main
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides scheduler's main loop
"""
import time
import logging
from importlib import import_module
import shellstreaming.master.master_struct as ms


def sched_loop(
    job_graph,
    worker_hosts,  # [todo] - not only worker's hostname but also
                   # [todo] - worker's resource info is important for scheduling decision.
    worker_port,

    sched_module_name,
    reschedule_interval_sec,
):
    """Scheduler main loop of stream processing
    """
    logger = logging.getLogger('TerminalLogger')

    # prepare each worker's JobRegistrar
    job_registrars = {}
    for worker in worker_hosts:
        job_registrars[worker] = ms.conn_pool[worker].root.JobRegistrar()
    # prepare scheduler module
    sched_module = import_module(sched_module_name)

    while True:
        # 0. check if any job is alredy finished (update ms.jobs_placement)
        ## collect finished-list from each worker
        finished_jobs = {}
        for worker in worker_hosts:
            job_registrar = job_registrars[worker]
            finished_jobs[worker] = job_registrar.finished_jobs()
        ## remove worker from ms.jobs_placement if it already finishes job
        for job_id in job_graph.nodes_iter():
            if job_id not in ms.jobs_placement:  # no worker is assigined for this job_id
                continue
            assigned_workers = ms.jobs_placement[job_id]
            for worker in assigned_workers:
                if job_id in finished_jobs[worker]:
                    assigned_workers.remove(worker)

        # 1. calculate next job placement from current job placement, machine resource usage, ...
        next_jobs_placement = sched_module.calc_job_placement(
            job_graph, worker_hosts, ms.jobs_placement,
            # machine resource, ...
        )   # [todo] - most important part in scheduling
        logger.debug('New job scheduling is calculated')

        # 2. finish scheduler loop if all jobs are finished
        # [fix] - waiting for at most `reschedule_interval_sec` after all jobs are really finished.
        # [fix] - better to be `push`ed from worker when worker has finished job.
        remaining_jobs = filter(lambda job_id: len(next_jobs_placement[job_id]) > 0, job_graph.nodes_iter())
        if remaining_jobs == []:
            logger.debug('Finished all jobs')
            break

        # 3. request next job placement to workers
        for job_id in job_graph.nodes_iter():
            job_placement    = set(ms.jobs_placement[job_id]) if job_id in ms.jobs_placement else set()
            workers_to_reg   = tuple(set(next_jobs_placement[job_id]) - job_placement)
            workers_to_unreg = tuple(job_placement - set(next_jobs_placement[job_id]))
            for worker in workers_to_reg:
                job_registrar = job_registrars[worker]
                job_registrar.register(job_id)
            for worker in workers_to_unreg:
                job_registrar = job_registrars[worker]
                job_registrar.unregister(job_id)
        ms.jobs_placement = next_jobs_placement

        # 4. sleep
        time.sleep(reschedule_interval_sec)
