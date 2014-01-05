# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.inputstream import RandIntIStream
from shellstreaming.operator import FilterSplitOperator
from shellstreaming.outputstream import LocalFileOStream


def main():
    randint_stream = api.IStream(RandIntIStream, (0, 100))
    lo_stream, hi_stream = api.Operator(
        FilterSplitOperator,
        (
            'num < 50',   # lo_stream
            'num >= 50',  # hi_stream
        ),
        randint_stream,
    )
    # lo_stream => {'根本': 'FilterSplitOperator_3', '先': None, 'edge_id': '1: num < 50'}
    api.OStream(LocalFileOStream, ('lo_stream.txt'), lo_stream, 'localhost')
    api.OStream(LocalFileOStream, ('hi_stream.txt'), hi_stream, 'localhost')

    # [todo] - api.* の返り値を生ストリームIDでなくて何かのclass objectにする
