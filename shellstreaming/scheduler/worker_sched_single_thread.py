# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.worker_sched_single_thread
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Instanciate all jobs w/ single thread
"""
import logging
from shellstreaming.core.batch_queue import BatchQueue


def update_instances(
        job_graph, registered_jobs,
        finished_jobs, job_instances,
        batch_queues
):
    """Execute, wait job instance thread.

    :param job_graph:       (reference only)
    :param registered_jobs: (reference only)
    :param finished_jobs: ws.finished_jobs (to be updated)
    :param job_instances: ws.job_instances (to be updated)
    :param batch_queues: ws.batch_queues (to be updated)
    """
    logger = logging.getLogger('TerminalLogger')

    # instanciate newly-registered jobs
    for job_id in registered_jobs:
        # launch not-yet-instanciated job
        if job_id not in job_instances or job_instances[job_id] == []:
            job_attr = job_graph.node[job_id]
            job_type, job_class = (job_attr['type'], job_attr['class'])
            job_args, job_kw    = (job_attr['args'], job_attr['kwargs'])
            # create input/output batch queues for job w/ job_id if not yet created.
            # Note that queue creation should be done in job instance level (not job level)
            # because even unregistered job's instance may have remaining task
            in_edges  = job_graph.in_stream_edge_ids(job_id)
            out_edges = job_graph.out_stream_edge_ids(job_id)
            for edge in in_edges + out_edges:
                if edge not in batch_queues:
                    batch_queues[edge] = BatchQueue()
            # launch job instance
            assert(job_type in ('istream', 'operator', 'ostream'))
            logger.debug('Launching job instance: %s' % (job_id))
            if job_type == 'istream':
                assert(len(out_edges) == 1 and len(in_edges) == 0)
                job_instance = job_class(
                    *job_args,
                    output_queue=batch_queues[out_edges[0]],
                    **job_kw
                )
            elif job_type == 'ostream':
                assert(len(out_edges) == 0 and len(in_edges) == 1)
                job_instance = job_class(
                    *job_args,
                    input_queue=batch_queues[in_edges[0]],
                    **job_kw
                )
            else:  # 'operator'
                assert(len(out_edges) >= 1 and len(in_edges) >= 1)
                job_instance = job_class(
                    *job_args,
                    input_queues={edge: batch_queues[edge] for edge in in_edges},
                    output_queues={edge: batch_queues[edge] for edge in out_edges},
                    **job_kw
                )
            # register launced job
            job_instances[job_id] = [job_instance]

    # check whether job instance has finished
    for job_id in set(registered_jobs) - set(finished_jobs):
        instance = job_instances[job_id][0]
        if instance.isAlive():
            continue

        # this job is finished.
        finished_jobs.append(job_id)
        logger.debug('Job instance of %s has finished!!' % (job_id))
        # [todo] - remove batch queue...
        # [todo] - but cannot done here because althouth upstream job has been finished,
        # [todo] - some batch might remain on the queue.
