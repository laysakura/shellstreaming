#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import shellstreaming


setup(
    name             = shellstreaming.__name__,
    description      = '[under development] A stream processor working with shell commands',
    long_description = open('README.rst').read(),
    url              = 'https://github.com/laysakura/shellstreaming',
    license          = 'LICENSE.txt',
    version          = shellstreaming.__version__,
    author           = 'Sho Nakatani',
    author_email     = 'lay.sakura@gmail.com',
    test_suite       = 'nose.collector',
    install_requires = shellstreaming.install_requires,
    tests_require    = [
        'nose',
        'coverage',
        'nose-cov',
    ],
    packages         = shellstreaming.packages,
    scripts          = [
        'bin/shellstreaming',
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
