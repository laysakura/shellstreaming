# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import RandInt
from shellstreaming.ostream import LocalFile


OUTPUT_FILE = '/tmp/01_RandInt.txt'


def main():
    randint_stream = api.IStream(RandInt, 0, 100, sleep_sec=1e-8, max_records=1000)
    api.OStream(randint_stream, LocalFile, OUTPUT_FILE, output_format='json', fixed_to=['localhost'])


def test():
    import json

    with open(OUTPUT_FILE) as f:
        for i, line in enumerate(f):
            record = json.loads(line)
            assert(0 <= int(record['num']) <= 100)
        assert(i + 1 == 1000)
