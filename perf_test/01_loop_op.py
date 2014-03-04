# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import RandInt
from shellstreaming.operator import Loop
from shellstreaming.ostream import LocalFile


OUTPUT_FILE  = '/tmp/00_benchmark.txt'
NUM_RECORDS      = 100000


def main():
    randint_stream = api.IStream(RandInt, 0, 100, sleep_sec=1e-7, max_records=NUM_RECORDS)
    null_stream = api.Operator([randint_stream], Loop)
    api.OStream(null_stream, LocalFile, OUTPUT_FILE, output_format='json', fixed_to=['cloko000'])
