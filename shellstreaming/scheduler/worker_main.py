# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.main
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides scheduler's main loop
"""
# standard modules
from threading import Thread
import time
from importlib import import_module
import logging

# my module
from shellstreaming.worker import worker_struct as ws


def sched_loop(
    sched_module_name,
    reschedule_interval_sec,
):
    """Scheduler main loop of stream processing
    """
    logger = logging.getLogger('TerminalLogger')
    sched_module = import_module(sched_module_name)

    # ** sub routines **
    def is_blocking_all_in_edges(job_id):
        is_blocking_all_q = True
        for edge_id in ws.JOB_GRAPH.in_stream_edge_ids(job_id):
            if edge_id not in ws.QUEUE_GROUPS:  # queue group is not yet registered, which means no input to block
                continue
            q = ws.QUEUE_GROUPS[edge_id]
            if q.is_working():
                is_blocking_all_q = False
                break
        return is_blocking_all_q

    def block_until_master_permits():
        while ws.BLOCKED_BY_MASTER:
            is_worker_blocked = True
            for job_id in set(ws.ASSIGNED_JOBS) - set(ws.finished_jobs):
                if not is_blocking_all_in_edges(job_id):
                    is_worker_blocked = False
            if is_worker_blocked:
                ws.ack_blocked = True
        ws.ack_blocked = False

    def declare_might_finished_jobs():
        for job_id in set(ws.ASSIGNED_JOBS) - set(ws.might_finished_jobs):
            if job_id not in ws.job_instance:
                # not even started any instance
                continue

            if not ws.job_instance[job_id].isAlive():
                ws.job_instance[job_id].join()
                # all instance are finished... then this job is *might be* finished!
                # it's possible new job instance is created by master on other nodes
                # after this `job_id` instance is creaeted locally.
                ws.might_finished_jobs.append(job_id)
                ## request master to newly create double-checking job instance if necessary
                del ws.job_instance[job_id]
                ws.ASSIGNED_JOBS.remove(job_id)
                logger.debug('Job %s might have finished ...? Asking master to double-check' % (job_id))

    # ** main loop **
    while True:
        sched_module.update_instances()
        declare_might_finished_jobs()

        # sleep, but be altert to `block` command by master
        t0 = time.time()
        while time.time() - t0 < reschedule_interval_sec:
            block_until_master_permits()
            time.sleep(0.01)


def start_sched_loop(sched_module_name, reschedule_interval_sec):
    """
    """
    t = Thread(target=sched_loop, args=(
        sched_module_name, reschedule_interval_sec))
    t.daemon = True
    t.start()
    return t
