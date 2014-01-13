# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import RandInt
from shellstreaming.operator import CountWindow, Sort
from shellstreaming.ostream import LocalFile


OUTPUT_FILE = '/tmp/04_Sort.txt'


def main():
    randint_stream = api.IStream(RandInt, 0, 100, max_records=1000, fixed_to=['cloko000'])
    randint_win = api.Operator(randint_stream, CountWindow, 3, slide_size=3, fixed_to=['cloko000'])
    sorted_win = api.Operator(randint_win, Sort, 'num')
    api.OStream(sorted_win, LocalFile, OUTPUT_FILE, output_format='json', fixed_to=['cloko000'])


def test():
    import json

    num_lines = 0
    with open(OUTPUT_FILE) as f:
        while True:
            try:
                first  = int(json.loads(next(f))['num'])
                second = int(json.loads(next(f))['num'])
                third  = int(json.loads(next(f))['num'])
                assert(first <= second <= third)
                num_lines += 3
            except StopIteration:
                break
    assert(num_lines == 999)
