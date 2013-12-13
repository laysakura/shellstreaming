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
from shellstreaming.logger import TerminalLogger as Logger


# prepare logger
logger = Logger(logging.DEBUG)


# important directories & files
scriptdir         = abspath(dirname(__file__))
pkg_name          = None
pkg_targz         = None


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

    global pkg_name, pkg_targz
    pkg_dir = _mk_latest_pkg()
    (pkg_name, pkg_targz) = _mk_targz(pkg_dir)

    already_packed = True


def deploy(cnfpath, deploy_dir):
    """Deploy :func:`pack`ed codes to remote hosts.

    :param cnfpath:    config file deployed to :param:`deploy_dir`
    :param deploy_dir: Relative path to deploy directory. It is put onto temporary direcory.
    """
    global already_packed, pkg_name, pkg_targz
    assert(already_packed)

    remote_deploy_dir = join(tempfile.gettempdir(), deploy_dir)

    # create deploy directory on remote host
    run('rm -rf %s' % (remote_deploy_dir))  # [fix] - not always remove
    run('mkdir %s'  % (remote_deploy_dir))

    # upload the config file
    put(cnfpath, remote_deploy_dir)

    # upload the source tarball to deploy directory on remote host
    put(pkg_targz, remote_deploy_dir)

    with cd(remote_deploy_dir):
        remote_pkg_targz = basename(pkg_targz)
        run('tar xzf %s' % (remote_pkg_targz))
        run('rm -f %s'   % (remote_pkg_targz))
        run('virtualenv .')
    with prefix('source %s' % join(remote_deploy_dir, 'bin', 'activate')), cd(join(remote_deploy_dir, pkg_name)):
        run('python setup.py install')  # installing into virtualenv's environment


def start_worker():
    """Start worker server via :func:`deploy`ed codes.

    When this task is called w/o preceeding :func:`deploy`, already-deployed codes are used.
    """
    global remote_deploy_dir, pkg_name
    with prefix('source %s' % join(remote_deploy_dir, 'bin', 'activate')), cd(join(remote_deploy_dir, pkg_name)):
        run('python %s async_start_server' % (join('shellstreaming', 'comm', 'worker.py')))


def _mk_latest_pkg():
    global scriptdir
    src_pkg_dir  = join(scriptdir, '..', '..', 'shellstreaming')  # [fix] - package name `shellstreaming` should not be hardcoded
    dest_pkg_dir = join(tempfile.gettempdir(), 'shellstreaming-latest-pkg')
    logger.info('Current package is <%s>. This is being deployed to worker nodes.' % (src_pkg_dir))

    local('rm -rf %s'   % (dest_pkg_dir))
    local('mkdir -p %s' % (dest_pkg_dir))
    local('cp -rf %s %s' % (src_pkg_dir, dest_pkg_dir))

    setup_py = join(dest_pkg_dir, 'setup.py')
    with open(setup_py, 'w') as f_setup_py:
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
        logger.debug('Written %s' % (setup_py))

    return dest_pkg_dir


def _mk_targz(pkg_dir):
    print(pkg_dir)
    with lcd(pkg_dir):
        pkg_name  = local('python setup.py --fullname', capture=True).strip()
        pkg_targz = join(pkg_dir, 'dist', pkg_name + '.tar.gz')
        local('rm -rf %s %s' % (pkg_name, pkg_targz))
        local('python setup.py sdist --formats=gztar', capture=False)
    return (pkg_name, pkg_targz)
