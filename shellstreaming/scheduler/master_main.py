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

    Loop of 1-3.

    1. calculate next job placement from current job placement, machine resource usage, ...
    2. request each worker next job placement
    3. sleep
    """
    logger = logging.getLogger('TerminalLogger')

    # prepare each worker's JobRegistrar
    job_registrars = {}
    for worker in worker_hosts:
        job_registrars[worker] = ms.conn_pool[worker].root.JobRegistrar()
    # prepare scheduler module
    sched_module = import_module(sched_module_name)

    while True:
        # 1. calculate next job placement from current job placement, machine resource usage, ...
        next_jobs_placement = sched_module.calc_job_placement(
            ms.jobs_placement,
            # machine resource, ...
        )   # [todo] - most important part in scheduling
        logger.debug('New job scheduling is calculated')

        # 2. request each worker next job placement
        for job_id in ms.jobs_placement.iterkeys():
            workers_to_reg   = tuple(set(next_jobs_placement[job_id]) - set(ms.jobs_placement[job_id]))
            workers_to_unreg = tuple(set(ms.jobs_placement[job_id])  - set(next_jobs_placement[job_id]))
            for worker in workers_to_reg:
                job_registrar = job_registrars[worker]
                job_registrar.register(job_id)
            for worker in workers_to_unreg:
                job_registrar = job_registrars[worker]
                job_registrar.unregister(job_id)

        # 3. sleep
        ms.jobs_placement = next_jobs_placement
        time.sleep(reschedule_interval_sec)
