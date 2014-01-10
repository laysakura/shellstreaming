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
import cPickle as pickle

# my module
from shellstreaming.worker import worker_struct as ws


def sched_loop(
    sched_module_name,
    reschedule_interval_sec,
):
    """Scheduler main loop of stream processing
    """
    sched_module = import_module(sched_module_name)
    while True:
        sched_module.update_instances()
        time.sleep(reschedule_interval_sec)


def start_sched_loop(sched_module_name, reschedule_interval_sec):
    """
    """
    t = Thread(target=sched_loop, args=(
        sched_module_name, reschedule_interval_sec))
    t.daemon = True
    t.start()
    return t
