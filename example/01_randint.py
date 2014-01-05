# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.inputstream import RandIntIStream
from shellstreaming.outputstream import LocalFileOStream


def main(job_graph):
    print('debug from user!!')  # この辺のprintが実はloggerによって吐かれる，みたいなの欲しい
    randint_stream = api.IStream(job_graph, RandIntIStream, (0, 100))  # 実際にinputstreamができる場所もシステムで勝手に決める
    api.OutputStream(job_graph, LocalFileOStream, ('/tmp/result.txt', ), randint_stream, 'localhost')  # => localhost:/tmp/result.txt
    # [todo] - outputの場所は「誰にoutputstreamを立てて欲しいか(worker server単位)」でなく
    # [todo] - 「誰のnodeにoutputが置かれて欲しいか(worker node単位)」になってるけど，これは妥当か
