# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.auto_deploy
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides `auto-deploy` feature.

    Call this script from `fabric`:

    .. code-block:: bash
        $ SHELLSTREAMING_CNF=/path/to/shellstreaming.cnf fab -f auto_deploy.py remote_clean pack deploy

"""
from fabric.api import *
from fabric.decorators import serial
from os import environ
from os.path import abspath, dirname, join, basename
import ConfigParser
import tempfile
from shellstreaming.logger import Logger
from shellstreaming.config import Config


# prepare logger
logger = Logger.instance()


# prepare config
cnfpath = environ.get('SHELLSTREAMING_CNF')
assert(cnfpath)
config  = Config.instance()
config.set_config_file(cnfpath)


# set user/host
env.hosts = config.get('worker', 'hosts').split(',')
try:
    env.user = config.get('worker', 'user')
except ConfigParser.NoOptionError as e:
    logger.info(e)
try:
    ssh_config_path     = config.get('worker', 'ssh_config_path')
    env.ssh_config_path = ssh_config_path
    env.use_ssh_config  = True
except ConfigParser.NoOptionError as e:
    logger.info(e)
    logger.warn('Use of `ssh_config` is strongly recommended for deploying worker scripts from master')
try:
    env.parallel = config.get('worker', 'parallel_deploy')
except ConfigParser.NoOptionError as e:
    logger.info(e)


# important directories & files
# basedir    = join(abspath(dirname(__file__)), '..', '..')
scriptdir  = abspath(dirname(__file__))
pkg_name  = None
pkg_targz = None
remote_deploy_dir = join(tempfile.gettempdir(), 'shellstreaming-deploy')


already_packed = False


@serial
def pack():
    # create a new source distribution as tarball (only once even if multiple remote hosts)
    global already_packed
    if already_packed:
        return

    global pkg_name, pkg_targz
    pkg_dir   = _mk_latest_pkg()
    (pkg_name, pkg_targz) = _mk_targz(pkg_dir)

    already_packed = True


def deploy():
    global already_packed, pkg_name, pkg_targz, remote_deploy_dir
    assert(already_packed)

    # create deploy directory on remote host
    run('rm -rf %s' % (remote_deploy_dir))
    run('mkdir %s'  % (remote_deploy_dir))

    # upload the source tarball to deploy directory on remote host
    put(pkg_targz, remote_deploy_dir)

    # (dist_tar, dist_dir) = (join(remote_deploy_dir, '%s.tar.gz' % (dist)), join(remote_deploy_dir, dist))
    with cd(remote_deploy_dir):
        remote_pkg_targz = basename(pkg_targz)
        run('tar xzf %s' % (remote_pkg_targz))
        run('rm -f %s'   % (remote_pkg_targz))
        run('virtualenv .')
    with prefix('source %s' % join(remote_deploy_dir, 'bin', 'activate')), cd(join(remote_deploy_dir, pkg_name)):
        run('python setup.py install')  # installing into virtualenv's environment


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
