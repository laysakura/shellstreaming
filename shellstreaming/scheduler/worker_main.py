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
    remote_queue_placement_getter,
):
    """Scheduler main loop of stream processing
    """
    sched_module = import_module(sched_module_name)
    while True:
        pickled_remote_queue_placement = remote_queue_placement_getter()
        sched_module.update_instances(pickle.loads(pickled_remote_queue_placement))
        time.sleep(reschedule_interval_sec)


def start_sched_loop(sched_module_name, reschedule_interval_sec, remote_queue_placement_getter):
    """
    :param remote_queue_placement_getter: funtion to return `master_struct.remote_queue_placement`
    """
    t = Thread(target=sched_loop, args=(
        sched_module_name, reschedule_interval_sec, remote_queue_placement_getter))
    t.daemon = True
    t.start()
    return t
