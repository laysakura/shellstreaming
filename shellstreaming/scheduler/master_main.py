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
        # fire worker if job is already finished
        ## ask each worker if you have finished job
        global_finished_jobs = []
        for worker in worker_hosts:
            job_registrar         = job_registrars[worker]
            pickled_finished_jobs = job_registrar.finished_jobs()
            finished_jobs         = pickle.loads(pickled_finished_jobs)
            map(lambda job_id: ms.job_placement.fire(job_id, worker), finished_jobs)
            global_finished_jobs += finished_jobs
        ## tell worker your job has already been done by others
        for job_id in job_graph.nodes_iter():
            for worker in ms.job_placement.assigned_workers(job_id):
                if job_id in global_finished_jobs:
                    logger.debug('oh %s! %s is alredy finished by other worker' % (worker, job_id))
                    ms.job_placement.fire(job_id, worker)

        # finish scheduler loop if all jobs are finished
        # [fix] - waiting for at most `reschedule_interval_sec` after all jobs are really finished.
        # [fix] - better to be `push`ed from worker when worker has finished job.
        remaining_jobs = filter(lambda job_id: not ms.job_placement.is_finished(job_id), job_graph.nodes_iter())
        if remaining_jobs == []:
            logger.debug('Finished all jobs')
            break

        # calculate next job placement from current job placement, machine resource usage, ...
        next_job_placement = sched_module.calc_job_placement(
            job_graph, worker_hosts, ms.job_placement,
            # machine resource, ...
        )   # [todo] - most important part in scheduling
        logger.debug('New job assignment is calculated: %s' % (next_job_placement))

        # update queue placement
        for job_id in job_graph.nodes_iter():
            out_edges = job_graph.out_stream_edge_ids(job_id)
            for out_edge in out_edges:
                ms.remote_queue_placement[out_edge] = next_job_placement.assigned_workers(job_id)
        map(lambda w: ms.conn_pool[w].root.update_remote_queue_placement(pickle.dumps(ms.remote_queue_placement)), worker_hosts)
        logger.debug('Remote queue placement is updated: %s' % (ms.remote_queue_placement))

        # request next job placement to workers
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

        # sleep
        time.sleep(reschedule_interval_sec)
