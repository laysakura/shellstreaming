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
        '<job id>': [<worker id>, <worker id>, ...],
        ...
    }
"""

conn_pool = {}
"""Connection pool to worker servers

.. code-block:: python
    {
        '<worker id>': <rpyc.connection object>,
        ...
    }
"""
