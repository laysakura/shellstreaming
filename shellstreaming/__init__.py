"""
    shellstreaming
    ~~~~~~~~~~~~~~

    :synopsis: Core package of shellstreaming
"""
from sys import version_info


__name__    = 'shellstreaming'
__version__ = '0.0.9'

install_requires = [
    'relshell',
    'importlib' if version_info < (2, 7, 0) else '',
    'rpyc',
    'fabric',
    'requests',
    'requests_oauthlib',
]
packages = [
    'shellstreaming',
    'shellstreaming.inputstream',
    'shellstreaming.operator',
    'shellstreaming.comm',
    'shellstreaming.bin',
]
scripts = [
    'shellstreaming/bin/shellstreaming_master',
    'shellstreaming/bin/shellstreaming_worker',
]
