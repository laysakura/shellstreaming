# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import RandInt
from shellstreaming.ostream import LocalFile


OUTPUT_FILE = '/tmp/01_randint.txt'


def main():
    randint_stream = api.IStream(RandInt, 0, 100, max_records=10)
    api.OStream('localhost', randint_stream, LocalFile, OUTPUT_FILE)  # => output is written to stdout by localhost's worker server


def test():
    with open(OUTPUT_FILE) as f:
        for line in f:
            assert(0 <= int(line) < 100)
