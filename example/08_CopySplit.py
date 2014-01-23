# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import RandInt
from shellstreaming.operator import CopySplit
from shellstreaming.ostream import LocalFile


OUTPUT_FILE_0 = '/tmp/08_CopySplit_0.txt'
OUTPUT_FILE_1 = '/tmp/08_CopySplit_1.txt'
OUTPUT_FILE_2 = '/tmp/08_CopySplit_2.txt'
NUM_RECORDS   = 100000


def main():
    randint_stream = api.IStream(RandInt, 0, 100, sleep_sec=1e-7, max_records=NUM_RECORDS)
    s0, s1, s2     = api.Operator([randint_stream], CopySplit, 3)
    api.OStream(s0, LocalFile, OUTPUT_FILE_0, output_format='json', fixed_to=['localhost'])
    api.OStream(s1, LocalFile, OUTPUT_FILE_1, output_format='json', fixed_to=['localhost'])
    api.OStream(s2, LocalFile, OUTPUT_FILE_2, output_format='json', fixed_to=['localhost'])


def test():
    import json

    for out_file in (OUTPUT_FILE_0, OUTPUT_FILE_1, OUTPUT_FILE_2):
        with open(out_file) as f:
            for i, line in enumerate(f):
                record = json.loads(line)
                assert(0 <= int(record['num']) <= 100)
            assert(i + 1 == NUM_RECORDS)
