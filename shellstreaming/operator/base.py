# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides abstract class for operators
"""
from abc import ABCMeta, abstractmethod


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
