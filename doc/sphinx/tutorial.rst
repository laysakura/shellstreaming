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
    $ cp support-files/sample-shellstreaming.cnf $HOME/.shellstreaming.cnf

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

    worker_hosts = a.example.com:10000,b.example.com:10000

    localhost_debug = no

    send_latest_codes_on_start = yes

    ssh_private_key = /home/yourname/.ssh/id_rsa


この設定では、 ``a.example.com`` , ``b.example.com`` の2台のノードでの並列処理が行われます。
``10000`` はTCPポート番号で、shellstreaming のワーカプロセスがこのポートでマスターや他ワーカからの接続を待ち受けます。
ファイアーウォール等の設定にご注意ください。
また、 ``shellstreaming`` コマンドを発行するノードにマスタープロセスが立ち上がります。

ワーカプロセスが立ち上がるそれぞれのノードには、マスタープロセスが立ち上がるノードからSSHログインが
可能である必要があります。
ログイン時には、``ssh_private_key`` で指定した秘密鍵が用いられます。

ここでは、ストリーム処理アプリケーションとして、 ``example/02_FilterSplit.py`` を使用します。
マシン環境に合わせるために、ソースを以下のように変更してください。

**example/02_FilterSplit.py**

.. code-block:: python

    ...
    api.OStream(lo_stream, LocalFile, LOW_OUTPUT_FILE,  output_format='json', fixed_to=['a.example.com:10000'])
    api.OStream(hi_stream, LocalFile, HIGH_OUTPUT_FILE, output_format='json', fixed_to=['a.example.com:10000'])
    ...

こうすることで、処理結果は ``a.example.com`` に集約されるようになります。

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
設定ファイルを ``send_latest_codes_on_start=no`` とすることで、起動時間を抑えることができます。

``example/02_FilterSplit.py`` は、最初に0から100までの乱数列を生成し、それが50より小さいかどうかで出力先を
``/tmp/02_FilterSplit_lo.txt``, ``/tmp/02_FilterSplit_hi.txt`` の2つに振り分けています。


Run more realistic applications
-------------------------------

ここでは、ストリーム処理系で実際に動作させるようなアプリケーションを取り上げます。
特に、シェルコマンドを活用した ``shellstreaming`` の強みが発揮されるようなアプリケーションを紹介しています。


Log analysis for Apache HTTP Server
###################################

Apache HTTP Server, 通称 ``apache2`` のアクセスログを解析するストリームアプリケーションを動作させてみましょう。
アプリケーションの動作の詳細は、 http://www.logos.ic.i.u-tokyo.ac.jp/~nakatani/pdf/master_thesis.pdf の3.1節をご覧ください。

ここでは、``a.example.com``, ``b.example.com`` の2台が ``/tmp/access.log`` にアクセスログを所有するものとし、
``c.example.com`` も加えた3台でログ解析を分散処理することとします。

まず、設定ファイルでワーカの設定を確認してください。

.. code-block:: python

    [shellstreaming]

    worker_hosts = a.example.com:10000,b.example.com:10000,c.example.com:10000

次に、ログ解析のためのストリーム処理アプリケーションを作成します。
といっても、``example/51_apache_log_analysis.py`` でほとんどできているので、あとは多少のパラメータを変更するだけです。

変更箇所は以下のとおりです。

**example/51_apache_log_analysis.py**

.. code-block:: python

    ...

    APACHE_LOG   = '/tmp/access.log'
    DAILY_ACCESS = '/tmp/51_apache_log_analysis_daily.txt'
    STATUS_CODES = '/tmp/51_apache_log_analysis_statuscode.txt'

    workers_with_access_log   = ['a.example.com:10000', 'b.example.com:10000']
    worker_to_collect_results = ['c.example.com:10000']

    ...

では、 ``localhost`` においてこのアプリケーションを開始します。
ただし、 ``a.example.com``, ``b.example.com`` に ``/tmp/access.log`` ファイルを予め作成しておいてください(空でも大丈夫です)。

.. code-block:: bash

    $ (a.example.com) touch /tmp/access.log
    $ (b.example.com) touch /tmp/access.log
    $ shellstreaming example/51_apache_log_analysis.py

このとき、shellstreaming は ``a.example.com`` と ``b.example.com`` の ``/tmp/access.log`` ファイルを監視し、
それに対して追記があった場合に、ログの解析処理をします。

試しに、 ``a.example.com`` においてログの追記を行なってみましょう。

.. code-block:: bash

    $ (a.example.com) echo '192.168.100.3 - - [03/01/2014:16:09:00 +0900] "GET / HTTP/1.1" 400 265 "-" "-"' >> /tmp/access.log

この追記されたログの集計結果は、 ``c.example.com`` の ``/tmp/51_apache_log_analysis_daily.txt`` と
``/tmp/51_apache_log_analysis_statuscode.txt`` にあります。
集約結果は追記毎に追加されていくので、 ``tail`` コマンドで確認しましょう。

.. code-block:: bash

    $ (c.example.com) tail -f /tmp/51_apache_log_analysis_daily.txt
    $ (c.example.com) tail -f /tmp/51_apache_log_analysis_statuscode.txt

更に追記を続けると、集約結果が更新されていくことが分かります。

.. code-block:: bash

    $ (a.example.com) echo '192.168.100.3 - - [03/01/2014:16:09:00 +0900] "GET / HTTP/1.1" 400 265 "-" "-"' >> /tmp/access.log
    $ (a.example.com) echo '192.168.100.3 - - [01/01/2014:16:09:00 +0900] "GET / HTTP/1.1" 400 265 "-" "-"' >> /tmp/access.log
    $ (a.example.com) echo '192.168.100.3 - - [02/01/2014:16:09:00 +0900] "GET / HTTP/1.1" 200 265 "-" "-"' >> /tmp/access.log

``b.example.com`` からも追記をしてみて、複数の(仮想の)Webサーバのログを集計できていることを確認してください。
