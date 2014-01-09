# -*- coding: utf-8 -*-
"""
    shellstreaming.master.master_struct
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides master struct
"""


job_placement = None
"""Instance of :class:`JobPlacement`"""

remote_queue_placement = {}
"""
.. code-block:: python
    {'<edge id>': ['<worker id who has the queue corresponding to edge id>', ...]}
"""
def remote_queue_placement_getter():
    """Called by worker: return current :data:`remote_queue_placement`"""
    import cPickle as pickle
    return pickle.dumps(remote_queue_placement)


conn_pool = {}
"""Connection pool to worker servers

.. code-block:: python
    {
        '<worker id>': <rpyc.connection object>,
        ...
    }
"""
