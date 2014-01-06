# -*- coding: utf-8 -*-
"""
    shellstreaming.worker.worker_struct
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker struct
"""


JOB_GRAPH = None
"""Job graph to refer. Only :func:`exposd_reg_job_graph` modifies this"""

REGISTERED_JOBS = []
"""Jobs to execute. Only :func:`exposd_register` and :func:`exposd_unregister` modify this"""

job_instances = {}
"""Jobs' instances

.. code-block:: python
    {
        '<job id>': [<job instance>, ...],
        ...
    }
"""

batch_queues = {}
"""Queue to put output batches

.. code-block:: python
    {
        '<StreamEdge.id>': <BatchQueue instance>,
        ...
    }
"""
