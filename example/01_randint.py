# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.inputstream import RandIntIStream
from shellstreaming.outputstream import StdoutOStream


def main():
    randint_stream = api.IStream(RandIntIStream, (0, 100))
    print('hellooooooooooooooooooooo', randint_stream)
    api.OStream(StdoutOStream, (), randint_stream, 'localhost')  # => output is written to stdout by localhost's worker server
