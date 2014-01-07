# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import RandInt
from shellstreaming.operator import FilterSplitOperator
from shellstreaming.ostream import LocalFile


def main():
    randint_stream = api.IStream(RandInt, 0, 100, max_records=1)
    lo_stream, hi_stream = api.Operator(
        randint_stream,
        FilterSplitOperator,
        'num < 50', 'num >= 50',
    )
    api.OStream('localhost', lo_stream, LocalFile, 'lo_stream.txt')
    api.OStream('localhost', hi_stream, LocalFile, 'hi_stream.txt')
