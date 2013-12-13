# -*- coding: utf-8 -*-
from nose.tools import *
from nose_parameterized import parameterized
import os
from os.path import abspath, dirname, join
import tempfile
import shlex
from subprocess import Popen


basedir    = join(abspath(dirname(__file__)), '..', '..')
scriptpath = join(basedir, 'comm', 'auto_deploy.py')


@parameterized([
    'pack deploy:cnfpath=%s,deploy_dir=%s' % (cnfpath, 'shellstreaming-deploy'),
])
def test_auto_deploy_tasks(tasks):
    global basedir, scriptpath
    (fd, cnfpath) = tempfile.mkstemp(prefix='shellstreaming-', suffix='.cnf')

    cmd = 'fab -f %(script)s -H %(hosts)s %(tasks)s' % {
        'script': scriptpath,
        'hosts': 'localhost',
        'tasks': tasks,
    }

    p = Popen(shlex.split(cmd), env=os.environ)
    exitcode = p.wait()
    eq_(exitcode, 0)

    os.remove(cnfpath)


def test_start_worker():
    
