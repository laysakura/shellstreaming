#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import shellstreaming


setup(
    name             = shellstreaming.__name__,
    description      = shellstreaming.__description__,
    long_description = open('README.rst').read(),
    url              = 'https://github.com/laysakura/shellstreaming',
    license          = 'LICENSE.txt',
    version          = shellstreaming.__version__,
    author           = 'Sho Nakatani',
    author_email     = 'lay.sakura@gmail.com',
    test_suite       = 'nose.collector',
    packages         = shellstreaming.packages,
    install_requires = (
        shellstreaming.install_requires +  # master & workers requirements
        [
            'fabric',
        ]  # master requirements
    ),
    tests_require = [
        'nose',
        'coverage',
        'nose-cov',
    ],
    scripts  = [
        'bin/shellstreaming',
    ],
    classifiers = '''
Programming Language :: Python
Development Status :: 4 - Beta
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 2.7
Operating System :: POSIX :: Linux
'''.strip().splitlines()
)
