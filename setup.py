#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup
import shellstreaming


setup(
    name          = 'shellstreaming',
    description   = '[under development] A stream processor working with shell commands',
    url           = 'https://github.com/laysakura/shellstreaming',
    license       = 'LICENSE.txt',
    version       = shellstreaming.__version__,
    author        = shellstreaming.__author__,
    author_email  = shellstreaming.__email__,
    test_suite    = 'nose.collector',
    requires      = [
    ],
    tests_require = [
        'nose',
        'coverage',
    ],
    packages      = [
        'shellstreaming',
        'shellstreaming.inputstream',
        'shellstreaming.test'
    ],
    scripts       = [
        # 'bin/foo.py'
    ],
    classifiers   = '''
Programming Language :: Python
Development Status :: 1 - Planning
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 2.7
Operating System :: POSIX :: Linux
'''.strip().splitlines()
)
