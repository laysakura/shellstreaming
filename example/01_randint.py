# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.inputstream import RandIntIStream
from shellstreaming.outputstream import LocalFileOStream


def main():
    randint_stream = api.IStream(RandIntIStream, (0, 100))
    api.OStream(LocalFileOStream, ('/tmp/result.txt', ), randint_stream, 'localhost')  # => localhost:/tmp/result.txt
    # [todo] - outputの場所は「誰にoutputstreamを立てて欲しいか(worker server単位)」でなく
    # [todo] - 「誰のnodeにoutputが置かれて欲しいか(worker node単位)」になってるけど，これは妥当か
