# -*- coding: utf-8 -*-

# to pass this test, "ssh -i $HOME/.ssh/id_rsa localhost" has to success.

import nose.tools as ns
import os
from os.path import abspath, dirname, join
import tempfile
import shlex
from subprocess import Popen
from shellstreaming.config import DEFAULT_CONFIG
from shellstreaming.util.comm import wait_worker_server, kill_worker_server


BASEDIR      = join(abspath(dirname(__file__)), '..', '..', 'shellstreaming')
SCRIPTPATH   = join(BASEDIR, 'autodeploy', 'auto_deploy.py')
WORKER_HOSTS = ['localhost']
WORKER_PORT  = int(DEFAULT_CONFIG['worker_port'])
SSH_PRIV_KEY = join(os.environ['HOME'], '.ssh', 'id_rsa')
LOG_PATH     = 'test_auto_deploy.txt'  # not created actually
cnfpath      = None


def setup():
    global cnfpath
    (fd, cnfpath) = tempfile.mkstemp(prefix='shellstreaming-', suffix='.cnf')
    with os.fdopen(fd, 'w') as f:
        f.writelines('[shellstreaming]')


def teardown():
    os.remove(cnfpath)


def test_deploy():
    global cnfpath

    cmd = 'fab -f %(script)s -H %(hosts)s %(tasks)s %(ssh_priv_key)s' % {
        'script'       : SCRIPTPATH,
        'hosts'        : ','.join(WORKER_HOSTS),
        'tasks'        : 'pack deploy:cnfpath=%s' % (cnfpath),
        'ssh_priv_key' : '-i ' + SSH_PRIV_KEY,
    }
    print(cmd)

    p = Popen(shlex.split(cmd), env=os.environ)
    exitcode = p.wait()
    ns.eq_(exitcode, 0)


def test_start_worker():
    cmd = 'fab -f %(script)s -H %(hosts)s %(tasks)s %(ssh_priv_key)s' % {
        'script'       : SCRIPTPATH,
        'hosts'        : ','.join(WORKER_HOSTS),
        'tasks'        : 'start_worker:cnfpath=%s,logpath=%s' % (cnfpath, LOG_PATH),
        'ssh_priv_key' : '-i ' + SSH_PRIV_KEY,
    }

    p = Popen(shlex.split(cmd), env=os.environ)
    exitcode = p.wait()
    ns.eq_(exitcode, 0)

    wait_worker_server(','.join(WORKER_HOSTS), WORKER_PORT)
    kill_worker_server(','.join(WORKER_HOSTS), WORKER_PORT)
