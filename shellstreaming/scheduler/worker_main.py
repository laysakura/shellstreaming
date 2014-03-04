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
    def declare_finished_jobs():
        for job_id in set(ws.ASSIGNED_JOBS) - set(ws.finished_jobs):
            if job_id not in ws.job_instance:
                # instance is not even started
                continue
            job_instance = ws.job_instance[job_id]
            if not job_instance.isAlive():
                # instance is finished
                job_instance.join()
                ws.finished_jobs.append(job_id)
                logger.debug('Job instance of %s has finished!!' % (job_id))
                del ws.job_instance[job_id]

    # ** main loop **
    while True:
        sched_module.update_instances()
        declare_finished_jobs()
        time.sleep(reschedule_interval_sec)


def start_sched_loop(sched_module_name, reschedule_interval_sec):
    """
    """
    t = Thread(target=sched_loop, args=(
        sched_module_name, reschedule_interval_sec))
    t.daemon = True
    t.start()
    return t
