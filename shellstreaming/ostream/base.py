# -*- coding: utf-8 -*-
"""
    shellstreaming.ostream.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides abstract ostream
"""
from shellstreaming.core.base_job import BaseJob


class Base(BaseJob):
    """Base class for ostream
    """

    def __init__(self, input_queue):
        """Constructor

        :param input_queue:  queue to input batches
        """
        self._batch_q = input_queue
        BaseJob.__init__(self)
