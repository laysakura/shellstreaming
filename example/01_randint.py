# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import RandInt
from shellstreaming.ostream import Stdout


def main():
    randint_stream = api.IStream(RandInt, (0, 100))
    api.OStream(Stdout, (), randint_stream, 'localhost')  # => output is written to stdout by localhost's worker server
