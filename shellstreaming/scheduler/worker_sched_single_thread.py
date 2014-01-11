# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.worker_sched_single_thread
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Instanciate all jobs w/ single thread
"""
# standard module
import logging

# my module
import shellstreaming.worker.worker_struct as ws
from shellstreaming.core.batch_queue import BatchQueue


def update_instances():
    """Execute, wait job instance thread.
    """
    logger = logging.getLogger('TerminalLogger')

    # instanciate newly-registered jobs
    for job_id in ws.ASSIGNED_JOBS:
        # launch not-yet-instanciated job
        if job_id not in ws.job_instances or ws.job_instances[job_id] == []:
            job_attr = ws.JOB_GRAPH.node[job_id]
            job_type, job_class = (job_attr['type'], job_attr['class'])
            job_args, job_kw    = (job_attr['args'], job_attr['kwargs'])
            # decide input queue of each edge
            in_edges = ws.JOB_GRAPH.in_stream_edge_ids(job_id)
            if job_type != 'istream':
                try:
                    in_queues = decide_input_queues(in_edges)
                except AttributeError:  # when not all in_edges have prepaired queue
                    logger.debug('%s could not find input queue... constructing? finished already?' % (job_id))
                    continue
            # create output batch queues for job w/ job_id if not yet created.
            # Note that queue creation should be done in job instance level (not job level)
            # because even unregistered job's instance may have remaining task
            out_edges = ws.JOB_GRAPH.out_stream_edge_ids(job_id)
            for edge in out_edges:
                if edge not in ws.local_queues:
                    ws.local_queues[edge] = BatchQueue()
            # launch job instance
            assert(job_type in ('istream', 'operator', 'ostream'))
            logger.debug('Launching job instance: %s' % (job_id))
            if job_type == 'istream':
                assert(len(out_edges) == 1 and len(in_edges) == 0)
                job_instance = job_class(
                    *job_args,
                    output_queue=ws.local_queues[out_edges[0]],
                    **job_kw)
            elif job_type == 'ostream':
                assert(len(out_edges) == 0 and len(in_edges) == 1)
                job_instance = job_class(
                    *job_args,
                    input_queue=in_queues.values()[0],
                    **job_kw)
            else:  # 'operator'
                assert(len(out_edges) >= 1 and len(in_edges) >= 1)
                job_instance = job_class(
                    *job_args,
                    input_queues=in_queues,
                    output_queues={edge: ws.local_queues[edge] for edge in out_edges},
                    **job_kw)
            # register launced job
            ws.job_instances[job_id] = [job_instance]

    # check whether job instance has finished
    for job_id in set(ws.ASSIGNED_JOBS) - set(ws.finished_jobs):
        if job_id not in ws.job_instances:
            continue
        instance = ws.job_instances[job_id][0]
        if instance.isAlive():
            continue

        ## job instance has finished.
        ## remove input queue if it is in local
        for in_edge in ws.JOB_GRAPH.in_stream_edge_ids(job_id):
            if in_edge in ws.local_queues:
                del ws.local_queues[in_edge]

        #全部の上流 queue からNoneをとらないと終われない!!
        instance.join()
        ws.job_instances[job_id].remove(instance)
        if not is_input_remain(job_id):
            # this job is finished (None is passed from input queue).
            ws.finished_jobs.append(job_id)
            logger.debug('Job instance of %s has finished!!' % (job_id))


def is_input_remain(job_id):
    in_edges = ws.JOB_GRAPH.in_stream_edge_ids(job_id)
    for in_edge in in_edges:
        if in_edge in ws.local_queues or len(ws.REMOTE_QUEUE_PLACEMENT[in_edge]) > 0:
            return True
    return False


def decide_input_queues(in_edges):
    """
    :returns:
        .. code-block:: python
            {
                in_edges[0]: <instance of BatchQueue or RemoteQueue>,
                ...
            }

    :raises: `AttributeError` when not all in_edges have prepaired queue
    """
    assert(len(in_edges) > 0)
    logger = logging.getLogger('TerminalLogger')

    in_queues = {}  # to return
    for in_edge in in_edges:
        ## optimization: prioritize local queue
        if in_edge in ws.local_queues:
            in_queues[in_edge] = ws.local_queues[in_edge]
            logger.debug('queue of "%s" is decided to be from %s' % (in_edge, ws.WORKER_ID))
            logger.debug('in_queues=%s' % (in_queues))
            return in_queues

        ## remote worker's queue might already be empty, or not setup yet.
        ## try all workers
        target_workers = set(ws.REMOTE_QUEUE_PLACEMENT[in_edge]) - set([ws.WORKER_ID])
        if len(target_workers) == 0:
            raise AttributeError('%s does not have actual queue setup' % (in_edge))
        for target_worker in target_workers:  ## [fix] - choose most cost-effective one first
            conn = ws.conn_pool[target_worker]
            try:
                in_queues[in_edge] = conn.root.queue_netref(in_edge)
            except EOFError as e:
                logger.debug('sometimes "connection closed by peer" happen here when connecting to %s ...' % (target_worker))  # [fi- why connection error?
            if in_edge in in_queues and in_queues[in_edge] is not None:
                logger.debug('queue of "%s" is decided to be from %s' % (in_edge, target_worker))
            else:
                raise AttributeError('%s does not have actual queue setup' % (in_edge))
    logger.debug('in_queues=%s' % (in_queues))
    return in_queues
