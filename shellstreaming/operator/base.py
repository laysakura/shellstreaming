# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides abstract class for operators
"""
from shellstreaming.core.base_job import BaseJob
from shellstreaming.util.decorator import abstractstatic


class Base(BaseJob):
    """Base class for operators"""

    def __init__(self):
        """Constructor
        """
        BaseJob.__init__(self)

    def interrupt(self, output_queues):
        """API to safely kill data-fetching thread.
        """
        map(lambda q: q.push(None), output_queues)
        BaseJob.interrupt(self)

    @abstractstatic
    def out_stream_edge_id_suffixes(*args):
        """Return suffixes of outcomming StreamEdge id

        Each element must be matched with StreamEdge id by using `str.endswith()`

        .. code-block:: python
            for suf in out_stream_edge_id_suffixes(...):
                if StreamEdge.id.endswith(suf):
                    ...

        :param *args: same as parameters of :func:`self.__init__()`
        """
        pass
