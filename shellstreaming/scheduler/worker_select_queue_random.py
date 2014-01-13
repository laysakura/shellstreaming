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
from shellstreaming.util.comm import rpyc_namespace


def select_remote_worker_to_pop(edge_id, workers_with_queue):
    assert(ws.WORKER_ID not in workers_with_queue)
    i      = random.randint(0, len(workers_with_queue) - 1)
    worker = workers_with_queue[i]
    return worker
