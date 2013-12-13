# -*- coding: utf-8 -*-
"""
    shellstreaming.config
    ~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides config values read from config file
"""
from os.path import expanduser, join, exists
from ConfigParser import SafeConfigParser as ConfigParser


class Config(object):
    """Provides configuration"""

    def __init__(self, config_file):
        """Constructor"""
        self._parser = ConfigParser()
        self._parser.read(config_file)

    def get(self, section, option):
        """Get config values"""
        return self._parser.get(section, option)
