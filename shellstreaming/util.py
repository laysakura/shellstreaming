# -*- coding: utf-8 -*-
"""
    shellstreaming.util
    ~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides utility
"""
from os.path import abspath, dirname, basename
import sys
from importlib import import_module


def import_from_file(path):
    """Import module specified by python file path

    :param path: path to python module file, which ends with `.py`
    :raises:     :class:`ImportError` when import failed
    """
    if not path.endswith('.py'):
        raise ImportError('File name must ends with `.py`: %s' % (path))
    sys.path.append(dirname(abspath(path)))
    return import_module(basename(path)[:-3])
