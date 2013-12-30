# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.auto_deploy
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides `auto-deploy` feature.

    Call this script from `fabric`.
    Refer to `test_auto_deploy.py` to see how to call this.
"""
from fabric.api import *
from fabric.decorators import serial
from os.path import abspath, dirname, join, basename
import logging
import tempfile
import sys

# use `../../shellstreaming` as package if it exists
# (to reflect changes on `../../shellstreaming/**.py` quickly if using `<github-repo>/shellstreaming/comm/auto_deploy.py`)
basedir = join(abspath(dirname(__file__)), '..', '..')
sys.path = [basedir] + sys.path
from shellstreaming.logger import setup_TerminalLogger


# prepare logger
setup_TerminalLogger(logging.DEBUG)


# important path
LOCAL_SRC_PKG      = join(abspath(dirname(__file__)), '..', '..', 'shellstreaming')
LOCAL_LATEST_PKG   = join(tempfile.gettempdir(), 'shellstreaming-latest-pkg')
LOCAL_MIN_SETUP_PY = join(LOCAL_LATEST_PKG, 'setup.py')
REMOTE_DEPLOY      = join(tempfile.gettempdir(), 'shellstreaming-deploy')
REMOTE_PKG_ROOT    = join(REMOTE_DEPLOY, 'shellstreaming-root')
REMOTE_WORKER_PY   = join(REMOTE_PKG_ROOT, 'shellstreaming', 'comm', 'worker.py')
REMOTE_VIRTUALENV_ACTIVATE = join(REMOTE_DEPLOY, 'bin', 'activate')


already_packed = False


@serial
def pack():
    """Pack seemingly-latest codes to tarball.

    :param cnfpath:    config file deployed to :param:`deploy_dir`
    :param deploy_dir: Relative path to deploy directory. It is put onto temporary direcory.
    """
    # create a new source distribution as tarball (only once even if multiple remote hosts)
    global already_packed
    if already_packed:
        return

    _mk_latest_pkg()
    _mk_targz()

    already_packed = True


def deploy(cnfpath=''):
    """Deploy :func:`pack`ed codes to remote hosts.

    :param cnfpath: config file deployed to :data:`REMOTE_DEPLOY`. if empty string, config file is not deployed.
    """
    global already_packed
    assert(already_packed)

    # create deploy directory on remote host
    run('rm -rf %s' % (REMOTE_DEPLOY))
    run('mkdir %s'  % (REMOTE_DEPLOY))

    # upload the config file
    if cnfpath != '':
        put(cnfpath, REMOTE_DEPLOY)

    # upload the source tarball to deploy directory on remote host
    put(_get_pkg_targz(), REMOTE_DEPLOY)

    with cd(REMOTE_DEPLOY):
        remote_pkg_targz = basename(_get_pkg_targz())
        run('tar xzf %s' % (remote_pkg_targz))
        run('mv %s %s'   % (_get_pkg_name(), REMOTE_PKG_ROOT))
        run('rm -f %s'   % (remote_pkg_targz))
        run('virtualenv .')
    with cd(REMOTE_PKG_ROOT):
        with prefix('source %s' % REMOTE_VIRTUALENV_ACTIVATE):
            run('python setup.py install')  # installing into virtualenv's environment


def start_worker(cnfpath):
    """Start worker server via :func:`deploy`ed codes.

    When this task is called w/o preceeding :func:`deploy`, already-deployed codes are used.

    :param worker_server_port: TCP port number to launch rpyc server on worker
    :param cnfpath: path to config file
    """
    with cd(REMOTE_PKG_ROOT):
        with prefix('source %s' % REMOTE_VIRTUALENV_ACTIVATE):
            run('python %(remote_worker_py)s --config=%(cnfpath)s' % {
                'remote_worker_py' : REMOTE_WORKER_PY,
                'cnfpath'          : cnfpath,
            })


def _mk_latest_pkg():
    logger = logging.getLogger('TerminalLogger')
    logger.info('Current package is <%s>. This is being deployed to worker nodes.' % (LOCAL_SRC_PKG))

    local('rm -rf %s'   % (LOCAL_LATEST_PKG))
    local('mkdir -p %s' % (LOCAL_LATEST_PKG))
    local('cp -rf %s %s' % (LOCAL_SRC_PKG, LOCAL_LATEST_PKG))

    with open(LOCAL_MIN_SETUP_PY, 'w') as f_setup_py:
        f_setup_py.write(
'''# -*- coding: utf-8 -*-
from setuptools import setup
import shellstreaming


setup(
    name             = shellstreaming.__name__,
    version          = shellstreaming.__version__,
    install_requires = shellstreaming.install_requires,
    packages         = shellstreaming.packages,
)
'''
        )
        logger.debug('Written %s' % (LOCAL_MIN_SETUP_PY))


def _mk_targz():
    with lcd(LOCAL_LATEST_PKG):
        local('rm -rf %s %s' % (_get_pkg_name(), _get_pkg_targz()))
        local('python setup.py sdist --formats=gztar', capture=False)


def _get_pkg_name():
    with lcd(LOCAL_LATEST_PKG):
        return local('python setup.py --fullname', capture=True).strip()


def _get_pkg_targz():
    return join(LOCAL_LATEST_PKG, 'dist', _get_pkg_name() + '.tar.gz')
