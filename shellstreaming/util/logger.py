# -*- coding: utf-8 -*-
"""
    shellstreaming.util.logger
    ~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides logger
"""
import sys
import logging
from logging.handlers import RotatingFileHandler
from rainbow_logging_handler import RainbowLoggingHandler


def setup_TerminalLogger(log_level, logger_name='TerminalLogger'):
    """Setup colorful logger

    *Usage*

    .. code-block:: python
        setup_TerminalLogger(logging.DEBUG)
        logger = logging.getLogger('TerminalLogger')
        logger.debug('hello')
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    handler = RainbowLoggingHandler(sys.stderr)
    logger.addHandler(handler)


def setup_FileLogger(log_level, log_path, max_log_bytes=100 * 1e6, logger_name='FileLogger'):
    """Setup logger which outputs to config-specified file

    :param log_level: e.g. `logging.DEBUG`, ...
    :param log_path:  path to log file
    :prram max_log_bytes: max log file size to make rotete files

    *Usage*

    .. code-block:: python
        setup_FileLogger(logging.DEBUG, '/tmp/shellstreaming-worker.log')
        logger = logging.getLogger('FileLogger')
        logger.debug('hello')    # => log is written to '/tmp/shellstreaming-worker.log'
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    handler = RotatingFileHandler(log_path)
    logger.addHandler(handler)
