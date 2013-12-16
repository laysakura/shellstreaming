# -*- coding: utf-8 -*-

# to pass this test, "ssh -i $HOME/.ssh/id_rsa localhost" has to be in success.

from nose.tools import *
import os
from os.path import abspath, dirname, join
import tempfile
import shlex
from subprocess import Popen
from shellstreaming.comm.util import wait_worker_server, kill_worker_server


basedir      = join(abspath(dirname(__file__)), '..', '..')
scriptpath   = join(basedir, 'comm', 'auto_deploy.py')
WORKER_HOSTS = ['localhost']
WORKER_PORT  = 19876
SSH_PRIV_KEY = join(os.environ['HOME'], '.ssh', 'id_rsa')


def test_deploy():
    global scriptpath
    (fd, cnfpath) = tempfile.mkstemp(prefix='shellstreaming-', suffix='.cnf')

    cmd = 'fab -f %(script)s -H %(hosts)s %(tasks)s %(ssh_priv_key)s' % {
        'script'       : scriptpath,
        'hosts'        : ','.join(WORKER_HOSTS),
        'tasks'        : 'pack deploy:cnfpath=%s' % (cnfpath),
        'ssh_priv_key' : '-i ' + SSH_PRIV_KEY,
    }

    p = Popen(shlex.split(cmd), env=os.environ)
    exitcode = p.wait()
    eq_(exitcode, 0)

    os.remove(cnfpath)


def test_start_worker():
    global scriptpath

    cmd = 'fab -f %(script)s -H %(hosts)s %(tasks)s %(ssh_priv_key)s' % {
        'script'       : scriptpath,
        'hosts'        : ','.join(WORKER_HOSTS),
        'tasks'        : 'start_worker:worker_server_port=%d' % (WORKER_PORT),
        'ssh_priv_key' : '-i ' + SSH_PRIV_KEY,
    }

    p = Popen(shlex.split(cmd), env=os.environ)
    exitcode = p.wait()
    eq_(exitcode, 0)

    wait_worker_server(','.join(WORKER_HOSTS), WORKER_PORT)
    kill_worker_server(','.join(WORKER_HOSTS), WORKER_PORT)
