# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import RandInt
from shellstreaming.operator import CountWindow, Sort
from shellstreaming.ostream import LocalFile


OUTPUT_FILE = '/tmp/07_CountWindow.py'


def main():
    randint_stream = api.IStream(RandInt, 0, 100, max_records=1000)
    randint_win    = api.Operator(
        randint_stream,
        CountWindow,
        3, slide_size=3
    )
    sorted_win = api.Operator(
        randint_win,
        Sort, 'num'
    )
    api.OStream('localhost', sorted_win, LocalFile, OUTPUT_FILE, output_format='json')


def test():
    import json

    with open(OUTPUT_FILE) as f:
        while True:
            try:
                first  = int(json.loads(next(f))['num'])
                second = int(json.loads(next(f))['num'])
                third  = int(json.loads(next(f))['num'])
                assert(first <= second <= third)
            except StopIteration:
                break
