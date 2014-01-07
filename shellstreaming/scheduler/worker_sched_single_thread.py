# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.worker_sched_single_thread
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Instanciate all jobs w/ single thread
"""
import logging
from shellstreaming.core.batch_queue import BatchQueue
import shellstreaming.worker.worker_struct as ws


def update_instances(job_graph, registered_jobs, job_instances):  # [todo] - finer grained methods?
    """

    :param job_graph:       (reference only)
    :param registered_jobs: (reference only)
    """
    logger = logging.getLogger('TerminalLogger')
    for job_id in registered_jobs:
        # launch not-yet-instanciated job
        if job_id not in job_instances or job_instances[job_id] == []:
            job_attr = job_graph.node[job_id]
            job_class, job_args, job_type = (job_attr['class'], job_attr['args'], job_attr['type'])
            # create input/output batch queues for job w/ job_id if not yet created.
            # Note that queue creation should be done in job instance level (not job level)
            # because even unregistered job's instance may have remaining task
            in_edges  = job_graph.in_stream_edge_ids(job_id)
            out_edges = job_graph.out_stream_edge_ids(job_id)
            for edge in in_edges + out_edges:
                if edge not in ws.batch_queues:
                    ws.batch_queues[edge] = BatchQueue()
            # launch job instance
            assert(job_type in ('istream', 'operator', 'ostream'))
            logger.debug('Launching job instance: %s' % (job_id))
            if job_type == 'istream':
                assert(len(out_edges) == 1 and len(in_edges) == 0)
                job_instance = job_class(*job_args, output_queue=ws.batch_queues[out_edges[0]])  # [todo] - use batch_time_ms?
            elif job_type == 'ostream':
                assert(len(out_edges) == 0 and len(in_edges) == 1)
                job_instance = job_class(*job_args, input_queue=ws.batch_queues[in_edges[0]])
            else:  # 'operator'
                assert(len(out_edges) >= 1 and len(in_edges) >= 1)
                job_instance = job_class(
                    *job_args,
                    input_queues={edge: ws.batch_queues[edge] for edge in in_edges},
                    output_queues={edge: ws.batch_queues[edge] for edge in out_edges}
                )
            # register launced job
            job_instances[job_id] = [job_instance]

        # [fix] - instanceの削除
        # jobにつき最後のinstanceがなくなったとき，queueを消すのも忘れずに
