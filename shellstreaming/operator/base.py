# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides abstract class for operators
"""
from abc import ABCMeta, abstractmethod
from shellstreaming.util import abstractstatic


class Base(object):
    """Base class for operators"""
    __metaclass__ = ABCMeta

    def __init__(self):
        """Constructor"""
        pass

    @abstractmethod
    def execute(self, batch):  # pragma: no cover
        """Execute operator

        :param batch: input
        :returns:     output batch
        """
        pass

    @abstractstatic
    def stream_names(*args):
        """Return names of output streams

        Each output stream must have different name.

        :param *args: same as parameters of :func:`self.__init__()`
        :returns: tuple of output stream names
        """
        pass
