# -*- coding: utf-8 -*-
"""
    shellstreaming.autodeploy.auto_deploy
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides `auto-deploy` feature.

    Call this script from `fabric`.
    Refer to `test_auto_deploy.py` to see how to call this.
"""
# standard moduels
from os.path import abspath, dirname, join, basename
import logging
import tempfile
import sys

# 3rd party modules
import fabric.api as fab
from fabric.api import env
from fabric.decorators import serial


# use `../../shellstreaming` as package if it exists
# (to reflect changes on `../../shellstreaming/**.py` quickly if using `<github-repo>/shellstreaming/autodeploy/auto_deploy.py`)
basedir = join(abspath(dirname(__file__)), '..', '..')
sys.path = [basedir] + sys.path
from shellstreaming.util.logger import setup_TerminalLogger


# prepare logger
setup_TerminalLogger(logging.DEBUG)


# important path
LOCAL_SRC_PKG      = join(abspath(dirname(__file__)), '..', '..', 'shellstreaming')
LOCAL_LATEST_PKG   = join(tempfile.gettempdir(), 'shellstreaming-latest-pkg')
LOCAL_MIN_SETUP_PY = join(LOCAL_LATEST_PKG, 'setup.py')
REMOTE_DEPLOY      = join(tempfile.gettempdir(), 'shellstreaming-deploy')
REMOTE_PKG_ROOT    = join(REMOTE_DEPLOY, 'shellstreaming-root')
REMOTE_WORKER_PY   = join(REMOTE_PKG_ROOT, 'shellstreaming', 'worker', 'worker.py')
REMOTE_VIRTUALENV_ACTIVATE = join(REMOTE_DEPLOY, 'bin', 'activate')


# flags to check task execution order
already_packed  = False


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


def deploy_config(cnfpath=''):
    """Deploy config file to remote hosts.

    :param cnfpath: config file deployed to :data:`REMOTE_DEPLOY`. if empty string, config file is not deployed.
    """
    # create deploy directory on remote host if not exists
    fab.run('mkdir -p %s'  % (REMOTE_DEPLOY))

    # upload the config file
    if cnfpath != '':
        fab.put(cnfpath, REMOTE_DEPLOY)


def deploy_codes():
    """Deploy :func:`pack`ed codes to remote hosts.

    :param cnfpath: config file deployed to :data:`REMOTE_DEPLOY`. if empty string, config file is not deployed.
    """
    assert(already_packed)

    # newly create deploy directory on remote host
    fab.run('rm -rf %s'  % (REMOTE_DEPLOY))
    fab.run('mkdir %s'  % (REMOTE_DEPLOY))

    # upload the source tarball to deploy directory on remote host
    fab.put(_get_pkg_targz(), REMOTE_DEPLOY)

    with fab.cd(REMOTE_DEPLOY):
        remote_pkg_targz = basename(_get_pkg_targz())
        fab.run('tar xzf %s' % (remote_pkg_targz))
        fab.run('mv %s %s'   % (_get_pkg_name(), REMOTE_PKG_ROOT))
        fab.run('rm -f %s'   % (remote_pkg_targz))
        fab.run('virtualenv .')
    with fab.cd(REMOTE_PKG_ROOT):
        with fab.prefix('source %s' % REMOTE_VIRTUALENV_ACTIVATE):
            fab.run('python setup.py install')  # installing into virtualenv's environment


def start_worker(cnfpath, logpath):
    """Start worker server via :func:`deploy`ed codes.

    When this task is called w/o preceeding :func:`deploy`, already-deployed codes are used.

    :param logpath: path to log file
    :param cnfpath: path to config file
    """
    with fab.cd(REMOTE_PKG_ROOT):
        with fab.prefix('source %s' % REMOTE_VIRTUALENV_ACTIVATE):
            fab.run('python %(remote_worker_py)s --hostname=%(hostname)s --config=%(cnfpath)s --log=%(logpath)s' % {
                'remote_worker_py' : REMOTE_WORKER_PY,
                'hostname'         : env.host,
                'cnfpath'          : cnfpath,
                'logpath'          : logpath,
            })


def _mk_latest_pkg():
    logger = logging.getLogger('TerminalLogger')
    logger.info('Current package is <%s>. This is being deployed to worker nodes.' % (LOCAL_SRC_PKG))

    fab.local('rm -rf %s'   % (LOCAL_LATEST_PKG))
    fab.local('mkdir -p %s' % (LOCAL_LATEST_PKG))
    fab.local('cp -rf %s %s' % (LOCAL_SRC_PKG, LOCAL_LATEST_PKG))

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
    with fab.lcd(LOCAL_LATEST_PKG):
        fab.local('rm -rf %s %s' % (_get_pkg_name(), _get_pkg_targz()))
        fab.local('python setup.py sdist --formats=gztar', capture=False)


def _get_pkg_name():
    with fab.lcd(LOCAL_LATEST_PKG):
        return fab.local('python setup.py --fullname', capture=True).strip()


def _get_pkg_targz():
    return join(LOCAL_LATEST_PKG, 'dist', _get_pkg_name() + '.tar.gz')
