# -*- coding: utf-8 -*-
"""
    shellstreaming.master.master_struct
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides master struct
"""


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

workers_who_might_have_active_outq = {}
"""
.. code-block:: python
    {
        job_id: [worker_id, ...],  # this job is processed by these workers at least once
        ...
    }
"""

finished_jobs = []
"""List of really finished jobs"""

lastly_assigned_jobs = []
"""List of lastly assigned jobs before really finish"""

conn_pool = {}
"""Connection pool to worker servers

.. code-block:: python
    {
        (<worker hostname>, <worker port number>): <rpyc.connection object>,
        ...
    }
"""
