# -*- coding: utf-8 -*-
from nose.tools import *
import os
from os.path import abspath, dirname, join
import tempfile
import shlex
from subprocess import Popen


basedir    = join(abspath(dirname(__file__)), '..', '..')
scriptpath = join(basedir, 'comm', 'auto_deploy.py')


def test_usage():
    global basedir, scriptpath
    (fd, cnfpath) = tempfile.mkstemp(prefix='shellstreaming-', suffix='.cnf')

    cmd = 'fab -f %(script)s -H %(hosts)s %(tasks)s' % {
        'script': scriptpath,
        'hosts': 'localhost',
        'tasks': 'pack deploy:cnfpath=%s,deploy_dir=%s' % (cnfpath, 'shellstreaming-deploy'),
    }

    p = Popen(shlex.split(cmd), env=os.environ)
    exitcode = p.wait()
    eq_(exitcode, 0)

    os.remove(cnfpath)
