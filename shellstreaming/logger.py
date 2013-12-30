# -*- coding: utf-8 -*-
"""
    shellstreaming.logger
    ~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides logger
"""
import sys
import logging
from logging.handlers import RotatingFileHandler
from rainbow_logging_handler import RainbowLoggingHandler


def setup_TerminalLogger(loglevel, logger_name='TerminalLogger'):
    """Setup colorful logger

    *Usage*

    .. code-block:: python
        setup_TerminalLogger(logging.DEBUG)
        logger = logging.getLogger('TerminalLogger')
        logger.debug('hello')
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(loglevel)
    handler = RainbowLoggingHandler(sys.stderr)
    logger.addHandler(handler)


class FileLogger(logging.Logger):
    """Provides logger which outputs to config-specified file"""

    def __init__(self, log_level, log_path, max_log_bytes):
        """Constructor

        :param log_level: e.g. `logging.DEBUG`, ...
        :param log_path:  path to log file
        :prram max_log_bytes: max log file size to make rotete files
        """
        logging.Logger.__init__(self, 'shellstreaming_FileLogger', log_level)
        handler = RotatingFileHandler(log_path)
        self.addHandler(handler)
