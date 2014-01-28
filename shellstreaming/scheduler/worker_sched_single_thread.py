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


def update_instances():
    """Execute, wait job instance thread.
    """
    logger = logging.getLogger('TerminalLogger')
    prev_job_instance = ws.job_instance.copy()  # used to check if any instance is newly finished/started

    # instanciate newly-registered jobs
    for job_id in set(ws.ASSIGNED_JOBS) - set(ws.finished_jobs):
        # launch not-yet-instanciated job
        if job_id not in ws.job_instance:
            job_attr = ws.JOB_GRAPH.node[job_id]
            job_type, job_class = (job_attr['type'], job_attr['class'])
            job_args, job_kw    = (job_attr['args'], job_attr['kwargs'])
            in_edges  = ws.JOB_GRAPH.in_stream_edge_ids(job_id)
            out_edges = ws.JOB_GRAPH.out_stream_edge_ids(job_id)

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
                    input_queue=ws.QUEUE_GROUPS[in_edges[0]],
                    **job_kw)
            else:  # 'operator'
                assert(len(out_edges) >= 1 and len(in_edges) >= 1)
                job_instance = job_class(
                    *job_args,
                    input_queues={edge: ws.QUEUE_GROUPS[edge] for edge in in_edges},
                    output_queues={edge: ws.local_queues[edge] for edge in out_edges},
                    **job_kw)
            # register launced job
            ws.job_instance[job_id] = job_instance

    if ws.job_instance != prev_job_instance:
        logger.debug('Updated job instance: %s' % (ws.job_instance))
