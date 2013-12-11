shellstreaming
==============

.. image:: https://travis-ci.org/laysakura/shellstreaming.png?branch=master
   :target: https://travis-ci.org/laysakura/shellstreaming

A stream processor working with shell commands

.. contents:: :local:

Installation
############

.. code-block:: bash

    $ pip install virtualenv shellstreaming
    $ vim ~/.shellstreaming.cnf


For developers
--------------

API reference
#############

Sphinx-powered documents are available on http://packages.python.org/shellstreaming


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


TODO
----

細かい話
########

- マスタワーカ間の通信はrpycで、ワーカ同士の通信はバッチの受け渡しがあるので生ソケットで

- group by で集約関数適用しない時はどんな結果が期待されているのだろう?

  - SQLite3だと，最後の行の値が返ってきた

    .. code-block:: sql

        select b, a from T group by b;  -- sum(a) とかだと直感的な結果．aだと，最後の行のaが返ってきた．


- 俺のシステムでリレーションを作るよりは，既存のDBからリレーションを取ってこれるadapterとリレーションにappendできるoutput opを作るほうが賢明．

  - システム的には飽くまでもRecordBatch同士の演算

- もしかしたらrecord一つ一つにtimestamp持たせるよりもbatchにtimespanだけ持たせればいいかも(?)

  - どんなアプリを使いたいか次第だし，両方のoptionがあったほうがいいだろうね

- 基本operatorを実装する

- recordがtimestampとlineage情報を持つようにする(?)

- data-fetcher とかいうのを producer に置き換える

- masterがconfigを見てworkerを起こす構成にしたい(わざわざworkerノードにログインしてデーモン起動のためのゴニョゴニョをしたくはない)

  - master -> worker の起動手続きはssh?

  - Zero-Deploy RPyC を使って，「マスタからコードを全部引っ張りだす機能を持ったクラス」を送り付ければ良さそう

    - Zero-Deploy RPyC は，PyPIにリリースされていないRPyC-3.3.0以上でしか動かない．しかもgithubから取ってきたのを無理やり試してもロクに動かなかった．後回し

- データソースからデータを取ってきてるワーカが死んだら・・・レプリ作る暇もなくデータロスが起こるね・・・


全体の展望
##########

- シェルオペレータを他の代数演算子と混ぜて、交換法則などを考える。その際、シェルコマンドに各種の制約を与える。

- マスタにオペレータ実行計画(JSON)をインプットし、マスタがものすっごい単純な規則で(インプットストリームも含め)オペレータをワーカに分配し、ワーカがじ実行するとこまでやる．
その後、フォールトトレランスを実装
更にその後、何かのDSLからオペレータ実行計画まで持っていくものを作り，
スケジューラも作り，
シェルオペレータのプロセス管理も頑張る


- どうやってデータを分配するか

  - HDFS
  - Spark Streamingはinput stream -> RDDという風にすぐさま分散している
  - 「ユーザから見たらどのワーカにデータが行くかはわからない」かつ「どうせストリームだし，裏側では勝手にデータが分散されている」みたいなのが一番目指すべき所．
  - naiveな分散のさせかたは，バッチ11をノード1に，バッチ12をノード2に，・・・みたいな感じだけど，そんな風にパイプラインチックにやるのがいいのか，どのバッチもどかんと分散するのがいいのか，それは分からない

- マスタ・ワーカなどの分散構成

  - 各種operator処理の分散

- 分散構成を定義するためにユーザがやらなければならないことを考える

  - zookeeperはUX糞だったなぁ・・・

- フォールトトレランス

  - マスタのトレランス
  - ワーカのトレランス
  - 実装しないまでも，「こう実装すれば大丈夫」という案は持っておくべき

- shellオペレータ

  - 通常のオペレータと同様，どこでオペレータ起動するか問題
  - 「オペレータの起動」と「オペレータのプロセスの起動」は別管理する必要がある
  - 「オペレータのプロセスの起動」あるいはサーバ化みたいなものをちゃんと自前管理する方策

- ワークフロー記述のDSL

  - 既存のものは本当に使えないか
  - 結局，JSONベース+webUIでセーブ時に毎回絵が更新みたいなのが嬉しいような気もする(GUIで細かいscript pathとか書きたくない気がするので)
