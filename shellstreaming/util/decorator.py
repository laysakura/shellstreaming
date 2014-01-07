# -*- coding: utf-8 -*-
"""
    shellstreaming.util.decorator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides custom decorators
"""


class abstractstatic(staticmethod):
    """provides @abstractstatic decorator"""
    __slots__ = ()

    def __init__(self, function):
        super(abstractstatic, self).__init__(function)
        function.__isabstractmethod__ = True
    __isabstractmethod__ = True
