# -*- coding: utf-8 -*-

# to pass this test, "ssh -i $HOME/.ssh/id_rsa localhost" has to be in success.

import nose.tools as ns
import os
from os.path import abspath, dirname, join
from shellstreaming.util.comm import kill_worker_server
from shellstreaming.master.master import _launch_workers


basedir        = join(abspath(dirname(__file__)), '..', '..')
AUTO_DEPLOY_PY = join(basedir, 'comm', 'auto_deploy.py')
WORKER_IDS   = ['localhost']
WORKER_PORT    = 20001
SSH_PRIV_KEY   = join(os.environ['HOME'], '.ssh', 'id_rsa')


def test__launch_workers():
    _launch_workers(WORKER_IDS, WORKER_PORT, ssh_priv_key=SSH_PRIV_KEY)
    for host in WORKER_IDS:
        kill_worker_server(host, WORKER_PORT)
