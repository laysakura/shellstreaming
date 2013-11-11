# -*- coding: utf-8 -*-
from nose.tools import *
import shellstreaming.config as config


@raises(IOError)
def test_no_config_file_found():
    config._read_config_file(('nosuchfile', ))
