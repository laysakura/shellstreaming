#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
import shellstreaming

setup(
    name         = 'ShellStreaming',
    version      = shellstreaming.__version__,
    description  = '[under development] A stream processor working with shell commands',
    requires     = [
        'nose',
    ],
    packages     = [
        'shellstreaming',
        'shellstreaming.inputstream',
    ],
    author       = shellstreaming.__author__,
    author_email = shellstreaming.__email__,
    url          = '',
    classifiers  = '''
Programming Language :: Python
Development Status :: 1 - Planning
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 2.7
Operating System :: POSIX :: Linux
'''.strip().splitlines()
)
