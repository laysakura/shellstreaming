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

workers_who_might_have_active_outq = {}
"""
.. code-block:: python
    {
        job_id: [worker_id, ...],  # this job is processed by these workers at least once
        ...
    }
"""

will_finish_jobs = []
"""List of jobs which will definitely be finished w/o further job instances"""

last_assignments = {}
"""
.. code-block:: python
    {
        job_id: [worker_id, ...],  # this job must be re-executed by all of these [worker_id, ...]
                                   # [] means assignment is accomplished
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
