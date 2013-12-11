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

    CONFIG_FILE_CANDIDATES = (
        expanduser(join('~', '.shellstreaming.cnf')),
        expanduser(join('~', '.shellstreaming', 'shellstreaming.cnf')),
    )
    """List of candidate config file locations.

    Only one is used as config file. Left one is more prioritized.
    """

    _instance = None

    def __init__(self, config_file):
        """
        .. warn::
            Do not use this function. Use `instance()` and `set_config_file()`.
        """
        self._config_file = None
        self._parser      = None

    @staticmethod
    def instance():
        """Returns the `Config` instance"""
        if Config._instance is None:
            Config._instance = Config(None)
        return Config._instance

    def get(self, section, option):
        """Get config values"""
        if self._parser is None:  # config is not parsed yet
            self._parser = self._read_config()
        return self._parser.get(section, option)

    def set_config_file(self, config_file):
        """Set specific config file"""
        assert(config_file is not None)
        self._config_file = config_file
        self._parser      = None  # reset parsed config

    @staticmethod
    def _clear():
        """Clear read configs (only for testing purpose)"""
        Config._instance = None

    def _read_config(self):
        if self._config_file is None:  # config file is not specified => read from default locations
            self._config_file = Config._find_a_default_config_file()
            if self._config_file is None:
                raise IOError('None of %s exists' % (', '.join(Config.CONFIG_FILE_CANDIDATES)))

        parser = ConfigParser()
        if not parser.read(self._config_file):
            raise IOError('Cannot read config file (%s)' % (self._config_file))
        return parser

    @staticmethod
    def _find_a_default_config_file():
        for conf in Config.CONFIG_FILE_CANDIDATES:
            if exists(conf):
                return conf
        return None
