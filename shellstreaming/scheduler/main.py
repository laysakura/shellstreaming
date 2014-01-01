# -*- coding: utf-8 -*-
"""
    shellstreaming.scheduler.main
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides scheduler's main loop
"""
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
    for job_id in job_graph.nodes():
        job = job_graph.node[job_id]
        print(job_id, job)
        stream = JobDispatcher(worker_hosts[0], worker_port, job['class'], job['args'])
    #     # dispatch(job, worker_hosts[0]])  # どうやってdispatchしたopをmigrateしよう?
    #     #                                  # これが実際に何をやってるかによって，実行プロファイルを得たり，それからまたdispatchを変えたりってコードが変わってくる
    stream.join()  # [todo] - wait only last job?
