# -*- coding: utf-8 -*-
"""
    shellstreaming.worker.worker_struct
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker struct
"""


# information master passes. used especially for worker local scheduling
WORKER_ID = None
"""Worker's id. Got from config file's hostname.
Only :func:`exposd_set_worker_id` modifies this

.. code-block:: python
    (<worker hostname>, <worker port number>)
"""

WORKER_NUM_DICT = {}
"""Provides integer unique number for each worker.

{worker_id: worker_num, ...}
Only :func:`exposd_set_worker_num_dict` modifies this
"""

JOB_GRAPH = None
"""Job graph to refer. Only :func:`exposd_reg_job_graph` modifies this"""

ASSIGNED_JOBS = []
"""Jobs to execute. Only :func:`exposd_register` and :func:`exposd_unregister` modify this"""

QUEUE_GROUPS = {}
"""{edge_id: QueueGroup()} structure. Only :func:`exposd_update_queue_groups` modifies this"""

BLOCKED_BY_MASTER = False
"""True only when master starts `stop the world` for changing job scheduling.
Only :func:`exposd_block` & :func:`exposd_unblock` modifies this"""

# for communicating information with master
might_finished_jobs = []
"""Jobs which are assigned by master and might be finished. Double checking from master is necessary before really finish.
"""

# data only worker reads/updates
conn_pool = {}
"""Connection pool to worker servers

.. code-block:: python
    {
        (<worker hostname>, <worker port number>): <rpyc.connection object>,
        ...
    }
"""

job_instance = {}
"""Jobs' instance

.. code-block:: python
    {
        '<job id>': <job instance>,
        ...
    }
"""

ack_blocked = False
"""True when worker has finished blocking asked by worker"""

# for communicating with other workers
local_queues = {}
"""Queue to put output batches

.. code-block:: python
    {
        '<StreamEdge.id>': <BatchQueue instance>,  # local queue instance
        ...
    }
"""
