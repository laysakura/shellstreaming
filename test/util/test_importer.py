# -*- coding: utf-8 -*-
import nose.tools as ns
from os.path import join, dirname, abspath
from shellstreaming.util.importer import import_from_file


def f():
    pass


def test_import_from_file():
    module = import_from_file(__file__)

    f = getattr(module, 'f', None)
    ns.ok_(f is not None)

    g = getattr(module, 'g', None)
    ns.ok_(g is None)


@ns.raises(ImportError)
def test_import_from_file_invalid_file1():
    import_from_file('no_such_file.py')


@ns.raises(ImportError)
def test_import_from_file_invalid_file2():
    readme = join(dirname(abspath(__file__)), '..', '..', 'README.rst')
    import_from_file(readme)
