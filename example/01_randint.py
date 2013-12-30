# -*- coding: utf-8 -*-
from shellstreaming.api import *
from shellstreaming.inputstream.randint import RandInt
from shellstreaming.outputstream.localfile import LocalFile


def main(job_graph):
    print('debug from user!!')  # この辺のprintが実はloggerによって吐かれる，みたいなの欲しい
    randint_stream = InputStream(job_graph, RandInt)  # 実際にinputstreamができる場所もシステムで勝手に決める
    OutputStream(job_graph, LocalFile, ('/tmp/result.txt', ), randint_stream, 'localhost')  # => localhost:/tmp/result.txt
