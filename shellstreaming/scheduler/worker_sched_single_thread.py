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


def update_instances(remote_queue_placement):
    """Execute, wait job instance thread.

    :param remote_queue_placement: snapshot of master_struct.remote_queue_placement
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
            try:
                in_queues = decide_input_queues(in_edges, remote_queue_placement)
            except AttributeError:  # when not all in_edges have prepaired queue
                continue            # too early to launch this job => next job

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

        # this job is finished.
        ws.finished_jobs.append(job_id)
        logger.debug('Job instance of %s has finished!!' % (job_id))
        # [todo] - remove batch queue...
        # [todo] - but cannot done here because althouth upstream job has been finished,
        # [todo] - some batch might remain on the queue.


def decide_input_queues(in_edges, remote_queue_placement):
    """
    :returns:
        .. code-block:: python
            {
                in_edges[0]: <instance of BatchQueue or RemoteQueue>,
                ...
            }

    :raises: `AttributeError` when not all in_edges have prepaired queue
    """
    logger = logging.getLogger('TerminalLogger')

    in_queues = {}  # to return
    for in_edge in in_edges:
        ## optimization: prioritize local queue
        if in_edge in ws.local_queues:
            in_queues[in_edge] = ws.local_queues[in_edge]
            logger.debug('queue of "%s" is decided to be from localhost' % (in_edge))
        else:
            ## remote worker's queue might already be empty, or not setup yet.
            ## try all workers
            target_workers = set(remote_queue_placement[in_edge]) - set([ws.WORKER_ID])
            for target_worker in target_workers:  ## [fix] - choose most cost-effective one first
                conn = ws.conn_pool[target_worker]
                in_queues[in_edge] = conn.root.queue_netref(in_edge)
                if in_queues[in_edge] is not None:
                    logger.debug('queue of "%s" is decided to be from %s' % (in_edge, target_worker))
        if in_edge not in in_queues or in_queues[in_edge] is None:
            raise AttributeError('%s does not have actual queue setup' % (in_edge))
    return in_queues
