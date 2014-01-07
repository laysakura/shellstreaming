# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import RandInt
from shellstreaming.operator import FilterSplit
from shellstreaming.ostream import LocalFile


LOW_OUTPUT_FILE  = '/tmp/06_FilterSplit_lo.txt'
HIGH_OUTPUT_FILE = '/tmp/06_FilterSplit_hi.txt'


def main():
    randint_stream = api.IStream(RandInt, 0, 100, max_records=1000)
    lo_stream, hi_stream = api.Operator(
        randint_stream,
        FilterSplit,
        'num < 50', 'num >= 50',
    )
    api.OStream('localhost', lo_stream, LocalFile, LOW_OUTPUT_FILE)
    api.OStream('localhost', hi_stream, LocalFile, HIGH_OUTPUT_FILE)


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
    assert((lo + 1) + (hi + 1) == 1000)
