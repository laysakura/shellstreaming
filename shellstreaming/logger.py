# -*- coding: utf-8 -*-
"""
    shellstreaming.logger
    ~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides logger
"""
import sys
import logging
from rainbow_logging_handler import RainbowLoggingHandler


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

    # [todo] - logrotate

    logfile = None
    """Log file stream"""

    def __init__(self, log_level, log_path):
        """Constructor

        :param log_level: e.g. `logging.DEBUG`, ...
        :param log_path:  path to log file
        """
        logging.Logger.__init__(self, 'shellstreaming_FileLogger', log_level)
        FileLogger.logfile = open(log_path, 'a')
        handler = RainbowLoggingHandler(FileLogger.logfile)
        self.addHandler(handler)
