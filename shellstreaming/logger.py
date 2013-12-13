# -*- coding: utf-8 -*-
"""
    shellstreaming.logger
    ~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides logger
"""
import sys
import logging
from rainbow_logging_handler import RainbowLoggingHandler
from logging.handlers import RotatingFileHandler


class TerminalLogger(logging.Logger):
    """Provides colorful logger which outputs to stderr"""

    def __init__(self, log_level):
        """Constructor

        :param log_level: e.g. `logging.DEBUG`, ...
        """
        logging.Logger.__init__(self, 'shellstreaming_TerminalLogger', log_level)
        handler = RainbowLoggingHandler(sys.stderr)
        self.addHandler(handler)


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
