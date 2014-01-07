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

    def __init__(self, input_queues, output_queues):
        """Constructor

        :param input_queues:  queue to pop input batches
        :param output_queues: queue to push output batches
        :type input_queues: {<StreamEdge id>: <BatchQueue instance>, ...}
        :type output_queues: same as :param:`input_queues`
        """
        BaseJob.__init__(self)

    def interrupt(self):
        """API to safely kill data-fetching thread.
        """
        self._batch_q.push(None)  # producer has end data-fetching
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
