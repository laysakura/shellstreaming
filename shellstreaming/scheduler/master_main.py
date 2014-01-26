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

    def collect_might_finished_assignments():
        # if at least 1 worker finishes `job_id`,
        # it means other workers also finish the `job_id` since
        # all workers share the same `QueueGroup` and they determine `finish` by asking `QueueGroup`
        might_finished_assignments = []
        for worker in workers:
            job_registrar              = job_registrars[worker]
            worker_might_finished_jobs = pickle.loads(job_registrar.might_finished_jobs())
            map(lambda j: might_finished_assignments.append((j, worker)), worker_might_finished_jobs)
        return might_finished_assignments

    def sleep_and_poll_finish():
        t0 = time.time()
        while True:
            # 全部の job が終わってたらスケジューラループを終了．
            # ms.will_finish_jobs に含まれていてもそのジョブは「終わることが確定している」だけで，
            # 「まだoutputを出しているinstanceを持っている」かもしれない．
            # 本当にジョブが終わったかを見る時は，ms.job_placement を見て，割当てワーカの有無を見る
            all_jobs = job_graph.nodes()
            really_finished_jobs = [j for j in all_jobs if ms.job_placement.is_finished(j) and j in ms.will_finish_jobs]
            # logger.critical('really_finished_jobs => %s, ms.job_placement => %s' % (really_finished_jobs, ms.job_placement))
            if set(all_jobs) == set(really_finished_jobs):
                for worker in workers:
                    qstat = rpyc_namespace(worker).queue_status()
                    logger.warn('[%s] qstat => %s' % (worker, qstat))
                raise StopIteration
            # start double-check whether workers' jobs are really finished
            might_finished_assignments = [(j, w) for j, w in collect_might_finished_assignments() if j not in really_finished_jobs]
            for mf_job, mf_worker in might_finished_assignments:
                ms.job_placement.fire(mf_job, mf_worker)

                # もう mf_job が終わることが確定しているなら，fire以外はすることがない
                if mf_job in ms.will_finish_jobs:
                    continue

                # istream does not need double-checking since it inputs data not from queue group
                # but from data sources
                if mf_job in job_graph.begin_nodes():
                    if mf_job not in ms.will_finish_jobs:
                        ms.will_finish_jobs.append(mf_job)
                        really_finished_jobs.append(mf_job)
                        logger.critical('"%s"' % (ms.job_placement))  # [fix] - 全部のistream instance終わってない
                        logger.debug('"%s" is finished' % (mf_job))  # [fix] - 全部のistream instance終わってない
                    continue

                # workers finish last assignment => really finish!
                if (mf_job, mf_worker) in ms.last_assignments:
                    logger.error('mf_job => "%s", will_finish_jobs => %s, last_assignments => %s' % (mf_job, ms.will_finish_jobs, ms.last_assignments))
                    assert(mf_job not in ms.will_finish_jobs)
                    ms.will_finish_jobs.append(mf_job)
                    ms.last_assignments.remove((mf_job, mf_worker))
                    logger.critical('ms.last_assignments => %s' % (ms.last_assignments))
                    logger.debug('"%s" will finish soon since every input queue is assured to be checked' % (mf_job))
                    continue

                # if all of pred jobs are finished,
                # order a worker to check if this `job` really takes all None from all possibly-active queues,
                # then this `job` is really finished
                pred_jobs = job_graph.predecessors(mf_job)
                if len(filter(lambda pred: pred in ms.will_finish_jobs, pred_jobs)) == len(pred_jobs):
                    if mf_job not in [j for j, w in ms.last_assignments]:
                        ms.last_assignments.append((mf_job, mf_worker))
                        logger.critical('ms.last_assignments => %s' % (ms.last_assignments))

                # re-assign mf_job to double-check
                ## QueueGroupをupdate
                queue_groups = create_queue_groups(ms.job_placement)
                for in_edge in job_graph.in_stream_edge_ids(mf_job):
                    logger.warn('in_edge = %s, ms.workers_who_might_have_active_outq = %s' % (in_edge, ms.workers_who_might_have_active_outq[in_edge]))
                    assert(len(ms.workers_who_might_have_active_outq[in_edge]) > 0)
                    queue_groups[in_edge] = QueueGroup(in_edge, ms.workers_who_might_have_active_outq[in_edge])
                if mf_job not in [j for j, w in ms.last_assignments]:
                    # まだ上流ジョブが終わってないなら，さっきまでこの`mf_job`をやらせていたワーカにもう一度やらせる
                    rpyc_namespace(mf_worker).update_queue_groups(pickle.dumps(queue_groups))
                    ms.job_placement.assign(mf_job, mf_worker)
                    job_registrars[mf_worker].register(mf_job)
                else:
                    # 上流ジョブ終わっていて `mf_job` の last_assignments も決まっていたらそいつにやらせる
                    for j, w in ms.last_assignments:
                        if mf_job == j:
                            last_assigned_worker = w
                            break
                    rpyc_namespace(last_assigned_worker).update_queue_groups(pickle.dumps(queue_groups))
                    ms.job_placement.assign(mf_job, last_assigned_worker)
                    job_registrars[last_assigned_worker].register(mf_job)
                    logger.warn('"%s" is lastly assigned to %s' % (mf_job, last_assigned_worker))

            # time to reschedule
            if time.time() - t0 >= reschedule_interval_sec:
                return
            time.sleep(0.1)

    def create_local_queues_if_necessary(job_placement):
        for worker in workers:
            out_edges_not_created_yet = []
            for job in job_placement.assigned_jobs(worker):
                # every worker who at least once instanciates `job` might have active output queue of `job` instance
                for out_edge in job_graph.out_stream_edge_ids(job):
                    if out_edge not in ms.workers_who_might_have_active_outq:
                        ms.workers_who_might_have_active_outq[out_edge] = []
                    if worker not in ms.workers_who_might_have_active_outq[out_edge]:
                        logger.debug('Queue of "%s" is being created on %s' % (out_edge, worker))
                        ms.workers_who_might_have_active_outq[out_edge].append(worker)
                        out_edges_not_created_yet.append(out_edge)

            rpyc_namespace(worker).create_local_queues(out_edges_not_created_yet)

    def create_queue_groups(job_placement):
        queue_groups = {}
        for job in job_graph.nodes_iter():
            for edge in job_graph.out_stream_edge_ids(job):
                assigned_workers   = job_placement.assigned_workers(job)
                queue_groups[edge] = QueueGroup(edge, assigned_workers)
        return queue_groups

    def update_queue_groups(job_placement):
        t0 = time.time()
        create_local_queues_if_necessary(job_placement)
        logger.error('create_local_queues_if_necessary: %f sec' % (time.time() - t0))
        t0 = time.time()
        queue_groups = create_queue_groups(job_placement)
        logger.error('create_queue_groups: %f sec' % (time.time() - t0))
        t0 = time.time()
        map(lambda w: rpyc_namespace(w).update_queue_groups(pickle.dumps(queue_groups)), workers)
        logger.error('rpyc.update_queue_groups: %f sec' % (time.time() - t0))

    def remove_finished_jobs(job_placement):
        for job_id in ms.will_finish_jobs:
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
        t_stop_the_world_sec0 = time.time()
        logger.debug('pausing all workers ...')
        # t0 = time.time()
        # pause_all_workers()  # sychnronous call. stop all workers' activity
        # logger.critical('pause_all_workers: %f sec' % (time.time() - t0))
        logger.debug('paused!')

        prev_job_placement = ms.job_placement.copy()  # for calling reg_unreg_jobs_to_workers() later
        remove_finished_jobs(ms.job_placement)

        t0 = time.time()
        next_job_placement = sched_module.calc_job_placement(
            job_graph, workers, ms.job_placement,
            # machine resource, ...
        )   # [todo] - most important part in scheduling
        logger.critical('calc_job_placement: %f sec' % (time.time() - t0))
        logger.debug('New job assignment is calculated: %s' % (next_job_placement))

        # update queue_groups in each worker
        t0 = time.time()
        update_queue_groups(next_job_placement)
        logger.critical('update_queue_groups: %f sec' % (time.time() - t0))

        # register/unregister jobs to workers
        t0 = time.time()
        reg_unreg_jobs_to_workers(next_job_placement, prev_job_placement)
        logger.critical('reg_unreg_jobs_to_workers: %f sec' % (time.time() - t0))
        ms.job_placement = next_job_placement

        # t0 = time.time()
        # resume_all_workers()  # start again all workers' activity
        # logger.critical('resume_all_workers: %f sec' % (time.time() - t0))
        t_stop_the_world_sec1 = time.time()
        logger.debug('resumed workers activity, %f sec stop-the-world' % (t_stop_the_world_sec1 - t_stop_the_world_sec0))
        # [todo] - shorter stop-the-world for performance

        # sleep & poll all workers whether they finished their jobs.
        # if all jobs in job graph are finished, scheduler loop can be safely finished here since
        # no job migration occur in this code path.
        try:
            sleep_and_poll_finish()
        except StopIteration:
            logger.debug('All jobs are finished!')
            return
