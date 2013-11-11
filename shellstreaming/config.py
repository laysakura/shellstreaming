# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.config
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides config values read from config file
"""
from os.path import expanduser, join
from ConfigParser import SafeConfigParser as ConfigParser


CONFIG_FILE = (
    expanduser(join('~', '.shellstreaming.cnf')),
    expanduser(join('~', '.shellstreaming', 'shellstreaming.cnf')),
)
"""List of candidate config file locations.

Only one is used as config file. Left one is more prioritized.
"""


def _read_config_file():
    """Read a config file from `CONFIG_FILE <#shellstreaming.config.CONFIG_FILE>`_

    :raises: `IOError` if no config file exists
    """
    found = False
    config = ConfigParser()
    for conf_file in CONFIG_FILE:
        if config.read([conf_file]):
            found = True
            break
    if not found:
        raise IOError('None of %s exists' % (', '.join(CONFIG_FILE)))
    return config


config = _read_config_file()
