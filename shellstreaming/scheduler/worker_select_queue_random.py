# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.worker_select_queue_random
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis:
"""
# standard module
import random

# my module
import shellstreaming.worker.worker_struct as ws


def select_remote_worker_to_pop(edge_id, workers_with_queue):
    assert(len(workers_with_queue) > 0)
    i      = random.randint(0, len(workers_with_queue) - 1)
    worker = workers_with_queue[i]
    return worker
