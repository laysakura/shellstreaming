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

shellstreamingは分散ストリーム処理系です。
複数のノードを用いてアプリケーションを並列動作させてみましょう。

まずは設定ファイルを編集します。

**$HOME/.shellstreaming.cnf**

.. code-block:: python

    [shellstreaming]

    worker_hosts = localhost,a.example.com:10000,b.example.com:10000

    localhost_debug = no

    send_latest_codes_on_start = yes

    ssh_private_key = /home/yourname/.ssh/id_rsa


この設定では、``localhost`` , ``a.example.com`` , ``b.example.com`` の3台のノードでの並列処理が行われます。
``10000`` はTCPポート番号で、shellstreaming のワーカプロセスがこのポートでマスターや他ワーカからの接続を待ち受けます。
``localhost`` にはポート番号が指定されていませんが、デフォルトで18871番がが使用されます。

それぞれのノードには、 ``ssh_private_key`` で指定した秘密鍵を用いたSSHログインが可能である必要があります。

では、実際に簡単なアプリケーションを並列動作させてみましょう。

.. code-block:: bash

    $ shellstreaming example/02_FilterSplit.py
    [2014-03-04 15:36:47,632] master.py main():50   Used config file: /home/nakatani/.shellstreaming.cnf
    [2014-03-04 15:36:47,632] master.py _launch_workers():210       Auto-deploy starts with this command:
    fab -f /home/nakatani/git/shellstreaming/shellstreaming/master/../autodeploy/auto_deploy.py -H localhost,cloko020,cloko021 pack deploy_codes deploy_config:cnfpath=/home/nakatani/.shellstreaming.cnf start_worker:cnfpath=/home/nakatani/.shellstreaming.cnf,logpath=/tmp/shellstreaming-worker-HOSTNAME-PORT.log -P -i /home/nakatani/.ssh/id_rsa_lab_nopass

    ...

    [2014-03-04 15:42:37,434] master_main.py sched_loop():174       All jobs are finished!
    [2014-03-04 15:42:37,434] master.py main():107  Finished all job execution. Killing worker servers...
    [2014-03-04 15:42:37,438] comm.py kill_worker_server():34       requested close worker server on localhost:18871 to close
    [2014-03-04 15:42:37,441] comm.py kill_worker_server():34       requested close worker server on a.example.com:10000 to close
    [2014-03-04 15:42:37,445] comm.py kill_worker_server():34       requested close worker server on b.example.com:10000 to close
    [2014-03-04 15:42:37,446] master.py main():122
    Finished all job execution.
    Execution time: 6.883384 sec.

    [2014-03-04 15:42:38,317] master.py _run_test():247     02_FilterSplit.test finished without any exception
    [2014-03-04 15:42:38,317] master.py main():129  passed test()!

最初のうちは、コマンドを走らせたノードから、ワーカを立ち上げるノードへSSH経由でコードを送る処理が続きます。
これが一段落すると、``example/02_FilterSplit.py`` に記述された実際の処理が走ります。

一度SSH経由でコードを送られたノードは、次回以降はそのコードを再利用することができます。
設定ファイルを ``send_latest_codes_on_start = no`` とすることで、起動時間を抑えることができます。

``example/02_FilterSplit.py`` は、最初に0から100までの乱数列を生成し、それが50より小さいかどうかで出力先を
``/tmp/02_FilterSplit_lo.txt``, ``/tmp/02_FilterSplit_hi.txt`` の2つに振り分けています。
