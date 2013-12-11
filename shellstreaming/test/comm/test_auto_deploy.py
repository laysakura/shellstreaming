# -*- coding: utf-8 -*-

# This test is supposed to be ignored in `setup.cfg`

from nose.tools import *
from os.path import abspath, dirname, join
import shlex
from subprocess import Popen


basedir    = join(abspath(dirname(__file__)), '..', '..')
scriptpath = join(basedir, 'comm', 'auto_deploy.py')


def test_usage():
    # To fully pass this test, edit 'shellstreaming/test/data/shellstreaming_test_auto_deploy02.cnf'
    # as ssh login succeeds
    global basedir, scriptpath
    confpath   = join(basedir, 'test', 'data', 'shellstreaming_test_auto_deploy02.cnf')

    p = Popen(shlex.split('/home/nakatani/.pyenv/shims/fab -f %s remote_clean pack deploy' % (scriptpath)),
              env={'SHELLSTREAMING_CNF': confpath})
    exitcode = p.wait()
    eq_(exitcode, 0)


def test_no_ssh_config_usage():
    # To fully pass this test, edit 'shellstreaming/test/data/shellstreaming_test_auto_deploy01.cnf'
    # as ssh login succeeds
    global basedir, scriptpath
    confpath   = join(basedir, 'test', 'data', 'shellstreaming_test_auto_deploy01.cnf')

    p = Popen(shlex.split('/home/nakatani/.pyenv/shims/fab -f %s remote_clean pack deploy' % (scriptpath)),
              env={'SHELLSTREAMING_CNF': confpath})
    exitcode = p.wait()
    eq_(exitcode, 0)
