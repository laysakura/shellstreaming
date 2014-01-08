# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.main
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides scheduler's main loop
"""
# standard module
import time
import logging
from importlib import import_module
import cPickle as pickle

# my module
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
        # 0. check if any job is alredy finished (update ms.job_placement)
        for worker in worker_hosts:
            job_registrar         = job_registrars[worker]
            pickled_finished_jobs = job_registrar.finished_jobs()
            finished_jobs         = pickle.loads(pickled_finished_jobs)
            map(lambda job_id: ms.job_placement.fire(job_id, worker), finished_jobs)

        # 1. finish scheduler loop if all jobs are finished
        # [fix] - waiting for at most `reschedule_interval_sec` after all jobs are really finished.
        # [fix] - better to be `push`ed from worker when worker has finished job.
        remaining_jobs = filter(lambda job_id: not ms.job_placement.is_finished(job_id), job_graph.nodes_iter())
        if remaining_jobs == []:
            logger.debug('Finished all jobs')
            break

        # 2. calculate next job placement from current job placement, machine resource usage, ...
        next_job_placement = sched_module.calc_job_placement(
            job_graph, worker_hosts, ms.job_placement,
            # machine resource, ...
        )   # [todo] - most important part in scheduling
        logger.debug('New job assignment is calculated: %s' % (next_job_placement))

        # 3. request next job placement to workers
        for job_id in job_graph.nodes_iter():
            workers_to_reg   = tuple(set(next_job_placement.assigned_workers(job_id)) -
                                     set(ms.job_placement.assigned_workers(job_id)))
            workers_to_unreg = tuple(set(ms.job_placement.assigned_workers(job_id)) -
                                     set(next_job_placement.assigned_workers(job_id)))
            for worker in workers_to_reg:
                job_registrar = job_registrars[worker]
                job_registrar.register(job_id)
            for worker in workers_to_unreg:
                job_registrar = job_registrars[worker]
                job_registrar.unregister(job_id)
        ms.job_placement = next_job_placement

        # 4. sleep
        time.sleep(reschedule_interval_sec)
