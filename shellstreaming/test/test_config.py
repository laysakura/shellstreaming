# -*- coding: utf-8 -*-
from nose.tools import *
from os.path import abspath, dirname, join
from shellstreaming.config import Config


TEST_CONFIG1 = join(abspath(dirname(__file__)), 'data', 'shellstreaming_test01.cnf')
TEST_CONFIG2 = join(abspath(dirname(__file__)), 'data', 'shellstreaming_test02.cnf')


def test_config_usage():
    try:
        config = Config.instance()
        # port = int(config.get('worker', 'port'))
    except IOError as e:
        # config file is not found in default locations... but ok
        pass


def test_use_specified_config():
    Config._clear()

    config = Config.instance()
    config.set_config_file(TEST_CONFIG1)
    eq_('test_val1', config.get('test_section', 'test_var'))


def test_singleton():
    Config._clear()

    config1 = Config.instance()
    config1.set_config_file(TEST_CONFIG1)
    eq_('test_val1', config1.get('test_section', 'test_var'))

    # singleton -> same config file is used
    config2 = Config.instance()
    eq_('test_val1', config2.get('test_section', 'test_var'))

    # new config file is specified
    config2.set_config_file(TEST_CONFIG2)
    eq_('test_val2', config2.get('test_section', 'test_var'))
    eq_('test_val2', config1.get('test_section', 'test_var'))


@raises(IOError)
def test_specified_config_file_not_found():
    Config._clear()

    config = Config.instance()
    config.set_config_file('no_such_config.cnf')
    config.get('test_section', 'test_var')


def test_default_config_file_found():
    Config._clear()

    prev_cand = Config.CONFIG_FILE_CANDIDATES
    Config.CONFIG_FILE_CANDIDATES = (TEST_CONFIG1, )

    config = Config.instance()
    eq_('test_val1', config.get('test_section', 'test_var'))

    Config.CONFIG_FILE_CANDIDATES = prev_cand


@raises(IOError)
def test_default_config_file_not_found():
    Config._clear()

    prev_cand = Config.CONFIG_FILE_CANDIDATES
    Config.CONFIG_FILE_CANDIDATES = ('', )

    config = Config.instance()
    try:
        config.get('test_section', 'test_var')
    except:
        Config.CONFIG_FILE_CANDIDATES = prev_cand
        raise
