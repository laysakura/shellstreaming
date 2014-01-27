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
    logger  = logging.getLogger('TerminalLogger')
    workers = tuple(workers)

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

    def total_records_in_qs():
        """Returns total records in all queues"""
        ret = 0
        for w in workers:
            qstat = pickle.loads(rpyc_namespace(w).queue_status())
            logger.warn('[%s] qstat: %s' % (w, qstat))
            ret += sum(qstat.values())
        return ret

    def sleep_and_poll_finish():
        t0 = time.time()
        while True:
            # 全部の job が終わってたらスケジューラループを終了．
            # ms.will_finish_jobs に含まれていてもそのジョブは「終わることが確定している」だけで，
            # 「まだoutputを出しているinstanceを持っている」かもしれない．
            # 本当にジョブが終わったかを見る時は，ms.job_placement を見て，割当てワーカの有無を見る
            all_jobs = job_graph.nodes()
            really_finished_jobs = [j for j in all_jobs if ms.job_placement.is_finished(j) and j in ms.will_finish_jobs]
            finish_sched_loop = set(really_finished_jobs) == set(all_jobs)
            if finish_sched_loop:
                finish_sched_loop = total_records_in_qs() == 0
            if finish_sched_loop:
                raise StopIteration
            # start double-check whether workers' jobs are really finished
            might_finished_assignments = collect_might_finished_assignments()
            might_finished_assignments = [(j, w) for j, w in might_finished_assignments if j not in really_finished_jobs]
            for mf_job, mf_worker in might_finished_assignments:
                ms.job_placement.fire(mf_job, mf_worker)
                logger.debug('%s reports %s might be finished. Double-check start ...' % (mf_worker, mf_job))

                # もう mf_job が終わることが確定しているなら，fire以外はすることがない
                if mf_job in ms.will_finish_jobs:
                    continue

                # istream does not need double-checking since it inputs data not from queue group
                # but from data sources
                if mf_job in job_graph.begin_nodes():
                    if mf_job not in ms.will_finish_jobs:
                        ms.will_finish_jobs.append(mf_job)
                        really_finished_jobs.append(mf_job)
                        logger.debug('"%s" is finished' % (mf_job))  # [fix] - 全部のistream instance終わってない
                    continue

                # workers finish last assignment => really finish!
                if mf_job in ms.last_assignments and mf_worker in ms.last_assignments[mf_job]:
                    ms.last_assignments[mf_job].remove(mf_worker)
                    if ms.last_assignments[mf_job] == []:
                        assert(mf_job not in ms.will_finish_jobs)
                        ms.will_finish_jobs.append(mf_job)
                        del ms.last_assignments[mf_job]
                        logger.debug('"%s" will finish soon since every input queue is assured to be checked' % (mf_job))
                    continue

                # if all of pred jobs are finished,
                # order a worker to check if this `job` really takes all None from all possibly-active queues,
                # then this `job` is really finished
                pred_jobs = job_graph.predecessors(mf_job)
                if len(filter(lambda pred: pred in ms.will_finish_jobs, pred_jobs)) == len(pred_jobs):
                    if mf_job not in ms.last_assignments:
                        workers_to_assign = [mf_worker]  # only might-finish worker is enough if no fixed_to
                        if job_graph.node[mf_job]['fixed_to'] is not None:
                            # fixed_to があるなら，その全員をアサインする
                            workers_to_assign = job_graph.node[mf_job]['fixed_to']
                        ms.last_assignments[mf_job] = workers_to_assign

                # re-assign mf_job to double-check
                ## QueueGroupをupdate
                queue_groups = create_queue_groups(ms.job_placement)
                for in_edge in job_graph.in_stream_edge_ids(mf_job):
                    assert(len(ms.workers_who_might_have_active_outq[in_edge]) > 0)
                    queue_groups[in_edge] = QueueGroup(in_edge, ms.workers_who_might_have_active_outq[in_edge])
                update_queue_groups(queue_groups)

                if mf_job not in ms.last_assignments:
                    # まだ上流ジョブが終わってないなら，さっきまでこの`mf_job`をやらせていたワーカにもう一度やらせる
                    ms.job_placement.assign(mf_job, mf_worker)
                    job_registrars[mf_worker].register(mf_job)
                    logger.debug('Pred job of %s is not finished. asking %s to launch %s instance' % (mf_job, mf_worker, mf_job))
                else:
                    # 上流ジョブ終わっていて `mf_job` の last_assignments も決まっていたらそいつにやらせる
                    workers_to_assign = ms.last_assignments[mf_job]
                    map(lambda w: ms.job_placement.assign(mf_job, w), workers_to_assign)
                    map(lambda w: job_registrars[w].register(mf_job), workers_to_assign)
                    logger.debug('Pred job of %s seems finished. asking %s to launch %s instance for last check' % (mf_job, workers_to_assign, mf_job))

            # time to reschedule
            if time.time() - t0 >= reschedule_interval_sec:
                return
            time.sleep(0.1)

    def create_local_queues_if_necessary(queue_groups):
        for worker in workers:
            edges_not_created_yet = []
            for edge, qgroup in queue_groups.iteritems():
                if worker in qgroup._workers_to_pop:
                    if edge not in ms.workers_who_might_have_active_outq:
                        ms.workers_who_might_have_active_outq[edge] = []
                    if worker not in ms.workers_who_might_have_active_outq[edge]:
                        ms.workers_who_might_have_active_outq[edge].append(worker)
                        edges_not_created_yet.append(edge)
            rpyc_namespace(worker).create_local_queues(edges_not_created_yet)

    def create_queue_groups(job_placement):
        queue_groups = {}
        for job in job_graph.nodes_iter():
            for edge in job_graph.out_stream_edge_ids(job):
                assigned_workers   = job_placement.assigned_workers(job)
                queue_groups[edge] = QueueGroup(edge, assigned_workers)
        return queue_groups

    def update_queue_groups(queue_groups):
        create_local_queues_if_necessary(queue_groups)
        map(lambda w: rpyc_namespace(w).update_queue_groups(pickle.dumps(queue_groups)), workers)

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
        prev_job_placement = ms.job_placement.copy()  # for calling reg_unreg_jobs_to_workers() later
        remove_finished_jobs(ms.job_placement)

        next_job_placement = sched_module.calc_job_placement(
            job_graph, workers, ms.job_placement,
            # machine resource, ...
        )   # [todo] - most important part in scheduling
        logger.debug('New scheduling is calculated: %s' % (next_job_placement))

        # update queue_groups in each worker
        queue_groups = create_queue_groups(next_job_placement)
        update_queue_groups(queue_groups)

        # register/unregister jobs to workers
        reg_unreg_jobs_to_workers(next_job_placement, prev_job_placement)
        ms.job_placement = next_job_placement

        # sleep & poll all workers whether they finished their jobs.
        # if all jobs in job graph are finished, scheduler loop can be safely finished here since
        # no job migration occur in this code path.
        try:
            sleep_and_poll_finish()
        except StopIteration:
            logger.debug('All jobs are finished!')
            return
