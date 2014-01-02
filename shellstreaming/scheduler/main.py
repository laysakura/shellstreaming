# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.main
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides scheduler's main loop
"""
import rpyc
from shellstreaming.comm.job_dispatcher import JobDispatcher


def main_loop(job_graph,
              worker_hosts,  # [todo] - not only worker's hostname but also
                             # [todo] - worker's resource info is important for scheduling decision.
              worker_port):
    """Main loop of stream processing
    """
    #あと，「inputstreamならいらないけど，outputstreamなら前のjobの情報が必要」とかなら，JobDispatcherも継承させるのがいいかも

    # dispatch inputstreams
    # [todo] - more performance consideration
    for job_id in job_graph.begin_nodes():
        job = job_graph.node[job_id]
        print(job_id, job)
        stream = JobDispatcher(worker_hosts[0], worker_port, job_id, job['class'], job['args'])
    #     # dispatch(job, worker_hosts[0]])  # どうやってdispatchしたopをmigrateしよう?
    #     #                                  # これが実際に何をやってるかによって，実行プロファイルを得たり，それからまたdispatchを変えたりってコードが変わってくる

    import time
    time.sleep(1)  # [fix] - soon after Dispatch, job_id is not yet registered to `ws.job_instances`

    # dispatch outputstreams
    for job_id in job_graph.end_nodes():
        # choose best worker to fetch input batch
        pred_worker = 'localhost'    # [fix] - scheduling
        conn = rpyc.connect(pred_worker, worker_port)    # [fix] - connection pool
        pred_job_id = job_graph.predecessors(job_id)[0]  # [fix] - when multiple pred jobs (union, join)
        gen_in_batches = get_in_batches_generator(conn, pred_job_id)

        job = job_graph.node[job_id]
        print(job_id, job)
        stream = JobDispatcher(worker_hosts[0], worker_port, job_id, job['class'], job['args'], gen_in_batches)

    stream.join()  # [todo] - wait only last job?


def get_in_batches_generator(conn, job_id):
    """Return generator of input batches

    :param conn: :class:`rpyc`'s connection object to a worker server
    :param job_id: job's id to fetch batches from
    """
    def gen():
        while True:
            yield conn.root.get_out_batch(job_id)
    return gen
