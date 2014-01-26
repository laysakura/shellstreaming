# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import RandInt
from shellstreaming.ostream import LocalFile


OUTPUT_FILE = '/tmp/01_RandInt.txt'
NUM_RECORDS = 100000


def main():
    # truncate file first
    with open(OUTPUT_FILE, 'w'):
        pass

    randint_stream = api.IStream(RandInt, 0, 100, sleep_sec=1e-8, max_records=NUM_RECORDS)
    api.OStream(randint_stream, LocalFile, OUTPUT_FILE, output_format='json', fixed_to=['cloko000'])


def test():
    import json

    with open(OUTPUT_FILE) as f:
        for i, line in enumerate(f):
            record = json.loads(line)
            assert(0 <= int(record['num']) <= 100)
        assert(i + 1 == NUM_RECORDS)
