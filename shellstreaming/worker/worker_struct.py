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

IN_QUEUE_SELECTION_MODULE = None
"""Module that include select_remote_worker_to_pop() function """

# for communicating information with master
finished_jobs = []
"""Jobs whose instance is finished.
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

# for communicating with other workers
local_queues = {}
"""Queue to put output batches

.. code-block:: python
    {
        '<StreamEdge.id>': <BatchQueue instance>,  # local queue instance
        ...
    }
"""
