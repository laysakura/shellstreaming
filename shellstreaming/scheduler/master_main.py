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
from shellstreaming.core.queue_group import QueueGroup
from shellstreaming.util.comm import rpyc_namespace


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

    # ** sub modules **
    def pause_all_workers():
        map(lambda w: rpyc_namespace(w).block(), worker_hosts)

    def resume_all_workers():
        map(lambda w: rpyc_namespace(w).unblock(), worker_hosts)

    def collect_finished_jobs():
        # if at least 1 worker finishes `job_id`,
        # it means other workers also finish the `job_id` since
        # all workers share the same `QueueGroup` and they determine `finish` by asking `QueueGroup`
        finished_jobs = set()
        for worker in worker_hosts:
            job_registrar         = job_registrars[worker]
            worker_finished_jobs  = pickle.loads(job_registrar.finished_jobs())
            finished_jobs         = finished_jobs or set(worker_finished_jobs)
        return finished_jobs

    def sleep_and_poll_finish():
        t0 = time.time()
        while True:
            # poll workers finished jobs
            finished_jobs = collect_finished_jobs()
            if len(set(job_graph.nodes()) - set(finished_jobs)) == 0:
                raise StopIteration
            # time to reschedule
            if time.time() - t0 >= reschedule_interval_sec:
                return
            time.sleep(0.1)

    def create_local_queues_if_necessary(job_placement):
        q_req = {}  # {'worker id': ['edge id to create', ...]}
        for worker in worker_hosts:
            out_edges = []
            for job in job_placement.assigned_jobs(worker):
                out_edges += job_graph.out_stream_edge_ids(job)
            rpyc_namespace(worker).create_local_queues_if_not_exist(out_edges)

    def create_queue_groups(job_placement):
        queue_groups = {}
        for job in job_graph.nodes_iter():
            for edge in job_graph.out_stream_edge_ids(job):
                assigned_workers   = job_placement.assigned_workers(job)
                queue_groups[edge] = QueueGroup(edge, assigned_workers)
        return queue_groups

    def update_queue_groups(job_placement):
        create_local_queues_if_necessary(job_placement)
        queue_groups = create_queue_groups(job_placement)
        map(lambda w: rpyc_namespace(w).update_queue_groups(pickle.dumps(queue_groups)), worker_hosts)

    def remove_finished_jobs(job_placement):
        for job_id in collect_finished_jobs():
            for w in job_placement.assigned_workers(job_id):
                job_placement.fire(job_id, w)

    def reg_unreg_jobs_to_workers(next_job_placement, current_job_placement):
        for job_id in job_graph.nodes_iter():
            workers_to_reg   = tuple(set(next_job_placement.assigned_workers(job_id)) -
                                     set(current_job_placement.assigned_workers(job_id)))
            workers_to_unreg = tuple(set(current_job_placement.assigned_workers(job_id)) -
                                     set(next_job_placement.assigned_workers(job_id)))
            for worker in workers_to_reg:
                job_registrar = job_registrars[worker]
                job_registrar.register(job_id)
            for worker in workers_to_unreg:
                job_registrar = job_registrars[worker]
                job_registrar.unregister(job_id)

    # ** main loop **
    while True:
        logger.debug('pausing all workers ...')
        pause_all_workers()  # sychnronous call. stop all workers' activity
        logger.debug('paused!')

        prev_job_placement = ms.job_placement.copy()  # for calling reg_unreg_jobs_to_workers() later
        remove_finished_jobs(ms.job_placement)

        next_job_placement = sched_module.calc_job_placement(
            job_graph, worker_hosts, ms.job_placement,
            # machine resource, ...
        )   # [todo] - most important part in scheduling
        logger.debug('New job assignment is calculated: %s' % (next_job_placement))

        # register/unregister jobs to workers
        reg_unreg_jobs_to_workers(next_job_placement, prev_job_placement)
        ms.job_placement = next_job_placement

        # update queue_groups in each worker
        update_queue_groups(ms.job_placement)

        resume_all_workers()  # start again all workers' activity
        logger.debug('resumed workers activity')

        # sleep & poll all workers whether they finished their jobs.
        # if all jobs in job graph are finished, scheduler loop can be safely finished here since
        # no job migration occur in this code path.
        try:
            sleep_and_poll_finish()
        except StopIteration:
            logger.debug('All jobs are finished!')
            return
