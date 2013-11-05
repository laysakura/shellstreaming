#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
# from pypi_release import Release


setup(
    # cmdclass      = {'release': Release},

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
        'nextversion',
    ],
    tests_require    = [
        'nose',
        'coverage',
    ],
    packages         = [
        'shellstreaming',
        'shellstreaming.inputstream',
        'shellstreaming.test'
    ],
    scripts          = [
        # 'bin/foo.py'
    ],
    classifiers      = '''
Programming Language :: Python
Development Status :: 1 - Planning
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 2.7
Operating System :: POSIX :: Linux
'''.strip().splitlines()
)
