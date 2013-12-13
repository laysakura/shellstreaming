# -*- coding: utf-8 -*-
from nose.tools import *
from os.path import abspath, dirname, join
from shellstreaming.config import Config


TEST_CONFIG1 = join(abspath(dirname(__file__)), 'data', 'shellstreaming_test01.cnf')
TEST_CONFIG2 = join(abspath(dirname(__file__)), 'data', 'shellstreaming_test02.cnf')


def test_config_usage():
    config1 = Config(TEST_CONFIG1)
    eq_('test_val1', config1.get('test_section', 'test_var'))

    config2 = Config(TEST_CONFIG2)
    eq_('test_val2', config2.get('test_section', 'test_var'))
