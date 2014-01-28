# -*- coding: utf-8 -*-
"""
    shellstreaming.worker.worker_server
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker process's server
"""
# standard module
import cPickle as pickle
import logging
import os
from importlib import import_module

# 3rd party module
import rpyc
import psutil

# my module
from shellstreaming.core.batch import Batch
from shellstreaming.worker import worker_struct as ws
from shellstreaming.core.batch_queue import BatchQueue
from shellstreaming.core.partitioned_batch_queue import PartitionedBatchQueue
from shellstreaming.core.remote_queue import RemoteQueue
from shellstreaming.scheduler.worker_main import start_sched_loop
from shellstreaming.worker.job_registrar import JobRegistrar


class WorkerServerService(rpyc.Service):
    """Worker process's server"""

    # `rpyc.utils.server.*Server`'s instance
    server = None

    # APIs for master
    exposed_JobRegistrar = JobRegistrar

    def exposed_kill(self):
        """Kill worker server"""
        WorkerServerService.server.close()
        WorkerServerService.server = None

    def exposed_init(self, worker_id, pickled_worker_num_dict, pickled_job_graph,
                     set_cpu_affinity,
                     sched_module_name, reschedule_interval_sec,
                     in_queue_selection_module_name,
                     check_datatype):
        ws.WORKER_ID                 = worker_id
        ws.WORKER_NUM_DICT           = pickle.loads(pickled_worker_num_dict)
        ws.JOB_GRAPH                 = pickle.loads(pickled_job_graph)
        ws.IN_QUEUE_SELECTION_MODULE = import_module(in_queue_selection_module_name)
        Batch.check_datatype         = check_datatype
        if set_cpu_affinity:
            set_affinity(ws.WORKER_ID, ws.WORKER_NUM_DICT)
        start_sched_loop(sched_module_name, reschedule_interval_sec)

    def exposed_update_queue_groups(self, pickled_queue_groups):
        """Updates ws.QUEUE_GROUPS"""
        ws.QUEUE_GROUPS = pickle.loads(pickled_queue_groups)

    def exposed_create_local_queues_if_not_exist(self, edge_ids):
        """Create local queues corresponding to :param:`edge_ids` if it is not yet created"""
        logger = logging.getLogger('TerminalLogger')
        for e in edge_ids:
            if e not in ws.local_queues.keys():
                # create BatchQueue or PartitionedBatchQueue
                logger.debug('creating local queue for %s' % (e))
                partition_key = ws.JOB_GRAPH.edgeattr_from_edgeid(e)['partition_key']
                if partition_key is None:
                    ws.local_queues[e] = BatchQueue()
                else:
                    src_j, dest_j = ws.JOB_GRAPH.src_dest_from_edgeid(e)
                    fixed_to = ws.JOB_GRAPH.node[dest_j]['fixed_to']
                    assert(fixed_to is not None)
                    assert(len(fixed_to) == len(ws.WORKER_NUM_DICT))  # [fix] - 現在，partition_key 指定の下流ジョブは全ワーカで馬鹿並列することにしかできない． queue_group.py の [fix] 参照
                    ws.local_queues[e] = PartitionedBatchQueue(len(fixed_to), partition_key)  # ここが，下流ジョブのfixed_to数になっていて欲しい
                logger.debug('Local queue for %s is created' % (e))

    def exposed_queue_status(self):
        return pickle.dumps({e: q.records() for e, q in ws.local_queues.iteritems()})

    # APIs for workers
    def exposed_queue_netref(self, stream_edge_id, min_records_in_aggregated_batches):
        """Pass wrapper of BatchQueue to be remotely accessed
        """
        q = ws.local_queues[stream_edge_id]
        return RemoteQueue(q, min_records_in_aggregated_batches)


def _ith_in_node(worker_id, worker_num_dict):
    """
    .. code-block: python
        >>> worker_num_dict = {('node0', 10000): 0, ('node0', 10001): 1, ('node1', 10000): 2, ('node0', 10002): 3}
        >>> _ith_in_node(('node0', 10002), worker_num_dict)
        2
        >>> _ith_in_node(('node1', 10000), worker_num_dict)
        0
    """
    node = worker_id[0]
    i    = 0
    for w, num in sorted(worker_num_dict.items(), key=lambda num: num[1]):
        if w == worker_id:
            return i
        if w[0] == node:
            i += 1
    raise KeyError('"%s:%s" does not in `worker_num_dict`: %s' % (worker_id[0], worker_id[1], worker_num_dict))


def set_affinity(worker_id, worker_num_dict):
    """Bind the worker to a cpu core"""
    logger = logging.getLogger('TerminalLogger')
    i      = _ith_in_node(worker_id, worker_num_dict)
    core   = i % psutil.NUM_CPUS
    p      = psutil.Process(os.getpid())
    p.set_cpu_affinity([core])
    logger.debug('%s:%s is `set_affinity`ed to CPU core %d' % (worker_id[0], worker_id[1], core))
