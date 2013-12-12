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
from os import chdir, environ
from os.path import abspath, dirname, join
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


# important directories
basedir    = join(abspath(dirname(__file__)), '..', '..')
deploy_dir = join(tempfile.gettempdir(), 'shellstreaming-deploy')


def remote_clean():
    global deploy_dir
    # [todo] - kill worker processes here
    run('rm -rf %s' % (deploy_dir))


already_packed = False


@serial
def pack():
    # create a new source distribution as tarball (only once even if multiple remote hosts)
    global already_packed
    if already_packed:
        return

    global basedir
    chdir(basedir)
    dist = local('python setup.py --fullname', capture=True).strip()
    local('rm -rf %s' % (dist))
    local('python setup.py sdist --formats=gztar', capture=False)

    already_packed = True


def deploy():
    # figure out the release name and version
    global basedir, deploy_dir
    chdir(basedir)
    dist = local('python setup.py --fullname', capture=True).strip()
    # create deploy directory on remote host
    run('mkdir %s' % (deploy_dir))
    # upload the source tarball to deploy directory on remote host
    put(join('dist', '%s.tar.gz' % (dist)), deploy_dir)

    (dist_tar, dist_dir) = (join(deploy_dir, '%s.tar.gz' % (dist)), join(deploy_dir, dist))
    with cd(deploy_dir):
        run('tar xzf %s' % (dist_tar))
        run('rm -f %s' % (dist_tar))
        run('virtualenv .')
    with prefix('source %s' % join(deploy_dir, 'bin', 'activate')), cd('%s' % (dist_dir)):
        run('python setup.py install')  # installing into virtualenv's environment
