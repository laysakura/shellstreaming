# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import RandInt
from shellstreaming.operator import FilterSplit
from shellstreaming.ostream import LocalFile


LOW_OUTPUT_FILE  = '/tmp/02_FilterSplit_lo.txt'
HIGH_OUTPUT_FILE = '/tmp/02_FilterSplit_hi.txt'
NUM_IN_REC       = 10000


def main():
    randint_stream = api.IStream(RandInt, 0, 100, max_records=NUM_IN_REC)
    lo_stream, hi_stream = api.Operator(
        randint_stream,
        FilterSplit,
        'num < 50', 'num >= 50',
    )
    api.OStream('cloko000', lo_stream, LocalFile, LOW_OUTPUT_FILE,  output_format='json')
    api.OStream('cloko000', hi_stream, LocalFile, HIGH_OUTPUT_FILE, output_format='json')


def test():
    import json

    # low
    with open(LOW_OUTPUT_FILE) as f:
        for lo, line in enumerate(f):
            record = json.loads(line)
            assert(0 <= int(record['num']) < 50)
    # high
    with open(HIGH_OUTPUT_FILE) as f:
        for hi, line in enumerate(f):
            record = json.loads(line)
            assert(50 <= int(record['num']) <= 100)
    assert((lo + 1) + (hi + 1) == NUM_IN_REC)
