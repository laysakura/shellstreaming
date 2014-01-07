# -*- coding: utf-8 -*-
"""
    shellstreaming.master.master_struct
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides master struct
"""


jobs_placement = {}
"""Which worker has been regstered job?

.. code-block:: python
    {
        '<job id>': [<worker id>, <worker id>, ...],  # running job
        '<job id>': [],                               # finished job
        ...
    }
    # <job id> not in jobs_placement => job not started yet
"""

conn_pool = {}
"""Connection pool to worker servers

.. code-block:: python
    {
        '<worker id>': <rpyc.connection object>,
        ...
    }
"""
