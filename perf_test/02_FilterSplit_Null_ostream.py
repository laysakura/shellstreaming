# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import RandInt
from shellstreaming.operator import FilterSplit
from shellstreaming.ostream import Null


NUM_RECORDS      = 100000


def main():
    randint_stream = api.IStream(RandInt, 0, 100, sleep_sec=1e-7, max_records=NUM_RECORDS)
    lo_stream, hi_stream = api.Operator([randint_stream], FilterSplit, 'num < 50', 'num >= 50')
    api.OStream(lo_stream, Null, fixed_to=['localhost'])
    api.OStream(hi_stream, Null, fixed_to=['localhost'])
