Tutorial
========

.. toctree::
   :maxdepth: 1

Installation
------------

サンプルアプリケーションはgithubレポジトリにありますので、まだcloneをしていない場合はcloneをしてください。

.. code-block:: bash

    $ git clone https://github.com/laysakura/shellstreaming

shellstreamingはPythonのパッケージであり、使うのにインストールする必要があります。
ソースからインストールする場合は、cloneしたレポジトリのroot directoryから下記のコマンドを
実行してください（Pythonのインストール、virtualenvの有無によりsudoが必要な場合があります）。

.. code-block:: bash

    $ python setup.py install

PyPIというPythonのパッケージ・レポジトリからダウンロードしてインストールすることもできます。

.. code-block:: bash

    $ pip install shellstreaming

.. warning::

    shellstreamingはPython 2.7以上を必要としています。Python 3をサポートしていません。

Run first example in localhost
------------------------------

shellstreamingで最初のアプリケーションを動かしてみます。
shellstreamingは分散ストリーム処理系ですが、まずは設定の容易なlocalhost-modeを使ってみましょう。

shellstreamingの動作には設定ファイルが必要です。
設定ファイルは ``$HOME/.shellstreaming.cnf`` に配置します。

.. code-block:: bash

    $ cd shellstreaming
    $ support-files/sample-shellstreaming.cnf $HOME/.shellstreaming.cnf

では、早速アプリケーションを動かします。

.. code-block:: bash

    $ shellstreaming example/01_RandInt.py
    ...
    [2014-03-04 10:56:37,464] master.py main():122
    Finished all job execution.
    Execution time: 4.766653 sec.

    [2014-03-04 10:56:38,257] master.py _run_test():247     01_RandInt.test finished without any exception
    [2014-03-04 10:56:38,257] master.py main():129  passed test()!

正しく動作していれば、このような出力が得られるはずです。

``example/01_RandInt.py`` アプリケーションは、0から100までの整数値をランダムに生成し、
それを ``/tmp/01_RandInt.txt`` というファイルに書き出します。
ファイルを開いて内容を確認してみてください。

また、その他の ``example/*.py`` もサンプルアプリケーションです。
動作を試してみてください。


Run shellstreaming in parallel mode
-----------------------------------
