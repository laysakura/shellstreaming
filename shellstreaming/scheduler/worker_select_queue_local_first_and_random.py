# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.worker_select_queue_local_first_and_random
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis:
"""
# standard module
import random

# my module
import shellstreaming.worker.worker_struct as ws


def select_remote_worker_to_pop(edge_id, workers_with_queue):
    assert(len(workers_with_queue) > 0)

    # optimization: if local worker is in workers_with_queue, select it
    if ws.WORKER_ID in workers_with_queue:
        return ws.WORKER_ID

    i      = random.randint(0, len(workers_with_queue) - 1)
    worker = workers_with_queue[i]
    return worker
