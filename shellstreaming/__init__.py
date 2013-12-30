"""
    shellstreaming
    ~~~~~~~~~~~~~~

    :synopsis: Core package of shellstreaming
"""
from sys import version_info


__name__        = 'shellstreaming'
__version__     = '0.0.12'
__description__ = '[under development] A stream processor working with shell commands'

install_requires = [
    'relshell',
    'importlib' if version_info < (2, 7, 0) else '',
    'argparse'  if version_info < (2, 7, 0) else '',
    'rpyc',
    'networkx',
    'requests',
    'requests_oauthlib',
]
packages = [
    'shellstreaming',
    'shellstreaming.inputstream',
    'shellstreaming.operator',
    'shellstreaming.comm',
]
