# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import IncInt
from shellstreaming.operator import CountWindow
from shellstreaming.ostream import LocalFile


OUTPUT_FILE = '/tmp/07_CountWindow.py'


def main():
    randint_stream = api.IStream(IncInt, max_records=6)
    randint_win    = api.Operator(
        randint_stream,
        CountWindow,
        3, slide_size=1
    )
    api.OStream('localhost', randint_win, LocalFile, OUTPUT_FILE, output_format='json')


def test():
    import json

    with open(OUTPUT_FILE) as f:
        # 1st window event
        assert(int(json.loads(next(f))['num']) == 0)

        # 2nd window event
        assert(int(json.loads(next(f))['num']) == 0)
        assert(int(json.loads(next(f))['num']) == 1)

        # 3rd window event
        assert(int(json.loads(next(f))['num']) == 0)
        assert(int(json.loads(next(f))['num']) == 1)
        assert(int(json.loads(next(f))['num']) == 2)

        # 4th window event
        assert(int(json.loads(next(f))['num']) == 1)
        assert(int(json.loads(next(f))['num']) == 2)
        assert(int(json.loads(next(f))['num']) == 3)

        # 5th window event
        assert(int(json.loads(next(f))['num']) == 2)
        assert(int(json.loads(next(f))['num']) == 3)
        assert(int(json.loads(next(f))['num']) == 4)

        # 6th window event
        assert(int(json.loads(next(f))['num']) == 3)
        assert(int(json.loads(next(f))['num']) == 4)
        assert(int(json.loads(next(f))['num']) == 5)
