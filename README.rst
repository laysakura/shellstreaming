shellstreaming
==============

.. image:: https://travis-ci.org/laysakura/shellstreaming.png?branch=master
   :target: https://travis-ci.org/laysakura/shellstreaming

A stream processor working with shell commands

.. contents:: :local:

Installation
------------

.. code-block:: bash

    $ pip install virtualenv shellstreaming
    $ cp config/sample-shellstreaming.cnf ~/.shellstreaming.cnf
    $ vim ~/.shellstreaming.cnf

Run examples
------------

.. code-block:: bash

    $ git clone https://github.com/laysakura/shellstreaming.git
    $ cd shellstreaming
    $ shellstreaming example/01_RandInt.py


API reference
-------------

Sphinx-powered documents are available on http://packages.python.org/shellstreaming


For developers
--------------

Building and uploading documents
################################

.. code-block:: bash

    $ ./setup.py build_sphinx
    $ browser doc/html/index.html
    $ ./setup.py upload_sphinx

Testing
#######

.. code-block:: bash

    $ ./setup.py nosetests
    $ browser htmlcov/index.html  # check coverage

Some tests depend too much on personal configuration;
one needs Twitter OAuth info and another needs access to remote machine via `ssh`.
To enable all of these tests, comment out the line starts with `ignore-files` in `setup.cfg`
and run `nosetests` again.

Uploading packages to PyPI
##########################

.. code-block:: bash

    $ emacs setup.py   # edit `version` string
    $ emacs CHANGES.txt
    $ ./setup.py sdist upload

Or use `zest.releaser <https://pypi.python.org/pypi/zest.releaser>`_, a convenient tool for repeated release cycles.

Thanks
------

- `modocache <https://github.com/modocache>`_ for a few pull requests!
