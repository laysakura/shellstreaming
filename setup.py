#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import version_info
from setuptools import setup


setup(
    name             = 'shellstreaming',
    description      = '[under development] A stream processor working with shell commands',
    long_description = open('README.rst').read(),
    url              = 'https://github.com/laysakura/shellstreaming',
    license          = 'LICENSE.txt',
    version          = '0.0.6',
    author           = 'Sho Nakatani',
    author_email     = 'lay.sakura@gmail.com',
    test_suite       = 'nose.collector',
    install_requires = [
        'relshell',
        'importlib' if version_info < (2, 7, 0) else '',
        'rpyc',
        'fabric',
        'requests',
        'requests_oauthlib',
    ],
    tests_require    = [
        'nose',
        'coverage',
        'nose-cov',
    ],
    packages         = [
        'shellstreaming',
        'shellstreaming.inputstream',
        'shellstreaming.operator',
        'shellstreaming.comm',
        'shellstreaming.test'
    ],
    scripts          = [
        # 'bin/foo.py'
    ],
    classifiers      = '''
Programming Language :: Python
Development Status :: 1 - Planning
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: Implementation :: PyPy
Operating System :: POSIX :: Linux
'''.strip().splitlines()
)
