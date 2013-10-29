shellstreaming
~~~~~~~~~~~~~~

A stream processor working with shell commands

For developers
==============

API documents
-------------

Sphinx-powered documents are available on `http://packages.python.org/shellstreaming/`_


Building and uploading documents
--------------------------------

.. code-block:: bash

    $ ./setup.py build_sphinx
    $ ls doc/html/index.html
    $ ./setup.py upload_sphinx

Testing
-------

.. code-block:: bash

    $ ./setup.py nosetests

Uploading packages to PyPI
--------------------------

.. code-block:: bash

    $ emacs shellstreaming/__init__.py   # edit __version__
    $ emacs CHANGES.txt
    $ ./setup.py sdist upload


TODO
====

- _internal_replをlistにしても動くことを確認するテスト
- 俺のシステムでリレーションを作るよりは，既存のDBからリレーションを取ってこれるadapterとリレーションにappendできるoutput opを作るほうが賢明．
  - システム的には飽くまでもRecordBatch同士の演算
- 基本operatorを実装する
- recordがtimestampとlineage情報を持つようにする(?)

- docstring
- 各種テスト
