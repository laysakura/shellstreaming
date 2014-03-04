# -*- coding: utf-8 -*-
"""
    shellstreaming.master.master_struct
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides master struct
"""


JOB_GRAPH = None

WORKER_IDS = []
"""List of worker host-port pairs

.. code-block:: python
    [
        ('node00', 12345),
        ...
    ]
"""

job_placement = None
"""Instance of :class:`JobPlacement`"""

local_queue_placement = {}
"""Master knows what queue each worker locally has.
If all of them are empty, stream processing has finished.

.. code-block:: python
    {
        (<worker hostname>, <worker port number>): [edge id, ...],
        ...
    }
"""

conn_pool = {}
"""Connection pool to worker servers

.. code-block:: python
    {
        (<worker hostname>, <worker port number>): <rpyc.connection object>,
        ...
    }
"""

MIN_RECORDS_IN_AGGREGATED_BATCHES = 0
"""optimization: batch aggregation size"""
