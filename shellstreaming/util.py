# -*- coding: utf-8 -*-
"""
    shellstreaming.util
    ~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides utility
"""
from os.path import abspath, dirname, basename
import sys
from importlib import import_module


class abstractstatic(staticmethod):
    """provides @abstractstatic decorator"""
    __slots__ = ()

    def __init__(self, function):
        super(abstractstatic, self).__init__(function)
        function.__isabstractmethod__ = True
    __isabstractmethod__ = True


def import_from_file(path):
    """Import module specified by python file path

    :param path: path to python module file, which ends with `.py`
    :raises:     :class:`ImportError` when import failed
    """
    module_name = basename(path)
    if path.endswith('.py'):
        module_name = module_name[:-len('.py')]
    elif path.endswith('.pyc'):
        module_name = module_name[:-len('.pyc')]
    else:
        raise ImportError('File name must ends with `.py` or `.pyc`: %s' % (path))
    sys.path.append(dirname(abspath(path)))
    return import_module(module_name)
