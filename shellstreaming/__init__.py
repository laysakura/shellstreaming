"""
    shellstreaming
    ~~~~~~~~~~~~~~

    :synopsis: Core package of shellstreaming
"""
from sys import version_info


__name__        = 'shellstreaming'
__version__     = '0.1.1'
__description__ = 'A stream processor working with shell commands'

install_requires = [
    'relshell',
    'importlib' if version_info < (2, 7, 0) else '',
    'argparse'  if version_info < (2, 7, 0) else '',
    'rpyc',
    'networkx',
    'pyhashxx',
    'psutil',
    'requests',
    'requests_oauthlib',
]
packages = [
    'shellstreaming',
    'shellstreaming.master',
    'shellstreaming.worker',
    'shellstreaming.operator',
    'shellstreaming.istream',
    'shellstreaming.ostream',
    'shellstreaming.jobgraph',
    'shellstreaming.scheduler',
    'shellstreaming.config',
    'shellstreaming.core',
    'shellstreaming.util',
    'shellstreaming.autodeploy',
    'shellstreaming.api',
]
