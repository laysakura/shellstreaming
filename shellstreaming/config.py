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


def _read_config_file(config_file):
    """Read a config file from `config_file`

    :param:  tuple of config file candidates
    :raises: `IOError` if no config file exists
    """
    found = False
    config = ConfigParser()
    for f in config_file:
        if config.read([f]):
            found = True
            break
    if not found:
        raise IOError('None of %s exists' % (', '.join(config_file)))
    return config


config = _read_config_file(CONFIG_FILE)
