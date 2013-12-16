# -*- coding: utf-8 -*-
"""
    shellstreaming.config
    ~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides config values read from config file
"""
from ConfigParser import SafeConfigParser as ConfigParser, NoSectionError, NoOptionError


class Config(object):
    """Provides configuration"""

    def __init__(self, config_file):
        """Constructor"""
        self._parser = ConfigParser()
        self._parser.read(config_file)

    def get(self, section, option):
        """Get config values

        :returns: `None` if config is undefined
        """
        try:
            return self._parser.get(section, option)
        except (NoSectionError, NoOptionError):
            return None
