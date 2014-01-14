# -*- coding: utf-8 -*-
"""
    shellstreaming.master.master_struct
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides master struct
"""


WORKER_HOSTS = []
"""List of worker ids"""

job_placement = None
"""Instance of :class:`JobPlacement`"""

conn_pool = {}
"""Connection pool to worker servers

.. code-block:: python
    {
        '<worker id>': <rpyc.connection object>,
        ...
    }
"""
