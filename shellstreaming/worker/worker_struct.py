# -*- coding: utf-8 -*-
"""
    shellstreaming.worker.worker_struct
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker struct
"""


# information master passes. used especially for worker local scheduling
WORKER_ID = None
"""Worker's id. Only :func:`exposd_set_worker_id` modifies this"""

JOB_GRAPH = None
"""Job graph to refer. Only :func:`exposd_reg_job_graph` modifies this"""

ASSIGNED_JOBS = []
"""Jobs to execute. Only :func:`exposd_register` and :func:`exposd_unregister` modify this"""

REMOTE_QUEUE_PLACEMENT = None
"""Remote queue to fetch batches. Only :func:`exposd_update_remote_queue_placement` modifies this"""

# for communicating information with master
finished_jobs = []
"""Jobs which are assigned by master and finished.
Here `finish` means input queue has pass `None`.
"""

# data only worker reads/updates
conn_pool = {}
"""Connection pool to worker servers

.. code-block:: python
    {
        '<worker id>': <rpyc.connection object>,
        ...
    }
"""

job_instances = {}
"""Jobs' instances

.. code-block:: python
    {
        '<job id>': [<job instance>, ...],
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
