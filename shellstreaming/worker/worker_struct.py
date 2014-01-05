# -*- coding: utf-8 -*-
"""
    shellstreaming.worker.worker_struct
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides worker struct
"""


JOB_GRAPH = None
"""Job graph to refer. Only :func:`exposd_reg_job_graph` modify this"""

registered_jobs = []
"""Jobs to execute"""

output_queues = {}
"""Queue to put output batches

.. code-block:: python
    {
        '<StreamEdge.id>': <BatchQueue instance>,
        ...
    }
"""
