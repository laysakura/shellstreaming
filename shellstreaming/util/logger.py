# -*- coding: utf-8 -*-
"""
    shellstreaming.util.logger
    ~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides logger
"""
import sys
import logging
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
    handler = RainbowLoggingHandler(sys.stderr, datefmt=None)
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(filename)s %(funcName)s():%(lineno)d\t%(message)s"))
    logger.addHandler(handler)
