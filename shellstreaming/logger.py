# -*- coding: utf-8 -*-
"""
    shellstreaming.logger
    ~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides logger
"""
import sys
import logging
from rainbow_logging_handler import RainbowLoggingHandler
from shellstreaming.config import Config


class TerminalLogger(object):
    """Provides colorful logger which outputs to stderr"""

    _instance = None

    def __init__(self):
        """
        .. warn::
            Do not use this function. Use `instance()`.
        """
        self._logger = logging.getLogger('shellstreaming_TerminalLogger')
        self._logger.setLevel(logging.DEBUG)    # [todo] - set level by config

        handler = RainbowLoggingHandler(sys.stderr)
        self._logger.addHandler(handler)

    @staticmethod
    def instance():
        """Returns the logger instance"""
        if TerminalLogger._instance is None:
            TerminalLogger._instance = TerminalLogger()
        return TerminalLogger._instance._logger


class FileLogger(object):
    """Provides logger which outputs to config-specified file"""

    # [todo] - logrotate

    logfile = open(Config.instance().get('worker', 'logfile'), 'a')
    """Log file stream"""

    _instance = None

    def __init__(self):
        """
        .. warn::
            Do not use this function. Use `instance()`.
        """
        self._logger = logging.getLogger('shellstreaming_FileLogger')
        self._logger.setLevel(logging.DEBUG)

        handler = RainbowLoggingHandler(FileLogger.logfile)
        self._logger.addHandler(handler)

    @staticmethod
    def instance():
        """Returns the logger instance"""
        if FileLogger._instance is None:
            FileLogger._instance = FileLogger()
        return FileLogger._instance._logger
