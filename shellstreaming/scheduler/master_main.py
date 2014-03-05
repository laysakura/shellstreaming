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
    workers,  # [todo] - not only worker's hostname but also
              # [todo] - worker's resource info is important for scheduling decision.

    sched_module_name,
    reschedule_interval_sec,
):
    """Scheduler main loop of stream processing
    """
    logger = logging.getLogger('TerminalLogger')

    # prepare each worker's JobRegistrar
    job_registrars = {}
    for w in workers:
        job_registrars[w] = ms.conn_pool[w].root.JobRegistrar()
    # prepare scheduler module
    sched_module = import_module(sched_module_name)

    # ** sub modules **
    def pause_all_workers():
        map(lambda w: rpyc_namespace(w).block(), workers)

    def resume_all_workers():
        map(lambda w: rpyc_namespace(w).unblock(), workers)

    def collect_finished_jobs():
        """Ask each worker finished job instances and return aggregated results.

        :returns: [(worker, finished job instance), ...]
        """
        finished_jobs = []
        for w in workers:
            job_registrar        = job_registrars[w]
            worker_finished_jobs = pickle.loads(job_registrar.finished_jobs())
            map(lambda j: finished_jobs.append((w, j)), worker_finished_jobs)
        return finished_jobs

    def collect_queue_status():
        ret = {}  # {worker: {edge: size of queue or None, ...}, ...}
        for w in workers:
            qstat = pickle.loads(rpyc_namespace(w).queue_status())
            logger.warn('[%s] qstat: %s' % (w, qstat))
            ret[w] = qstat
        return ret

    def join_all_instances():
        while not ms.job_placement.are_all_finished():
            remove_finished_jobs(ms.job_placement)
            time.sleep(0.01)
        logger.debug('all job instances are finished!')

    def sleep_and_poll_finish():
        t0 = time.time()
        while True:
            time.sleep(0.5)

            # poll queue status of every worker to check wheter streaming processing has ended
            assert(len(ms.local_queue_placement) > 0)  # at least one local queue is created in main loop

            qstat = collect_queue_status()
            # all workers who has at least a local queue reply queue status
            assert(set(qstat.keys()) == set(ms.local_queue_placement.keys()))

            all_q_empty = True
            for w, edges in ms.local_queue_placement.iteritems():
                assert(len(edges) == len(qstat[w]))  # w replies all local queues info
                for e in edges:
                    qsize = qstat[w][e]
                    if qsize is not None:
                        all_q_empty = False
                        break
                if not all_q_empty:
                    break

            if all_q_empty:
                # ok, all queues emit last batch!
                # join all instances finally!
                logger.debug('joining all job instances ...')
                join_all_instances()
                raise StopIteration

            # time to reschedule?
            if time.time() - t0 >= reschedule_interval_sec:
                return

    def create_local_queues_if_necessary(job_placement):
        for worker in workers:
            if worker not in ms.local_queue_placement:
                # first local queue for worker
                ms.local_queue_placement[worker] = []

            out_edges = []
            for job in job_placement.assigned_jobs(worker):
                out_edges += job_graph.out_stream_edge_ids(job)
            rpyc_namespace(worker).create_local_queues_if_not_exist(out_edges)

            # master memorize newly created edge
            for e in out_edges:
                if e not in ms.local_queue_placement[worker]:
                    ms.local_queue_placement[worker].append(e)

    def create_queue_groups(job_placement):
        queue_groups = {}
        for job in job_graph.nodes_iter():
            for edge in job_graph.out_stream_edge_ids(job):
                assigned_workers   = job_placement.assigned_workers(job)
                queue_groups[edge] = QueueGroup(edge, assigned_workers, ms.MIN_RECORDS_IN_AGGREGATED_BATCHES)
        return queue_groups

    def update_queue_groups(job_placement):
        create_local_queues_if_necessary(job_placement)
        queue_groups = create_queue_groups(job_placement)
        map(lambda w: rpyc_namespace(w).update_queue_groups(pickle.dumps(queue_groups)), workers)

    def remove_finished_jobs(job_placement):
        for w, j in collect_finished_jobs():
            job_placement.fire(j, w)

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
        prev_job_placement = ms.job_placement.copy()  # for calling reg_unreg_jobs_to_workers() later
        remove_finished_jobs(ms.job_placement)

        next_job_placement = sched_module.calc_job_placement(
            job_graph, workers, ms.job_placement,
            # machine resource, ...
        )   # [todo] - most important part in scheduling
        logger.debug('New scheduling is calculated: %s' % (next_job_placement))

        # update queue_groups in each worker
        update_queue_groups(next_job_placement)

        # register/unregister jobs to workers
        reg_unreg_jobs_to_workers(next_job_placement, prev_job_placement)
        ms.job_placement = next_job_placement

        # sleep & poll all queues whether they are all empty
        try:
            sleep_and_poll_finish()
        except StopIteration:
            logger.debug('All jobs are finished!')
            return
