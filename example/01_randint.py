# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import RandIntIStream
from shellstreaming.ostream import StdoutOStream


def main():
    randint_stream = api.IStream(RandIntIStream, (0, 100))
    api.OStream(StdoutOStream, (), randint_stream, 'localhost')  # => output is written to stdout by localhost's worker server
