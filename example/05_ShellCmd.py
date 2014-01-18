# -*- coding: utf-8 -*-
import re
from shellstreaming import api
from shellstreaming.istream import RandInt
from shellstreaming.operator import ShellCmd
from shellstreaming.ostream import LocalFile


OUTPUT_FILE = '/tmp/05_ShellOperator.txt'
NUM_RECORDS = 100000


def main():
    randint_stream = api.IStream(RandInt, 0, 100, sleep_sec=1e-7, max_records=NUM_RECORDS)
    cat_stream = api.Operator(
        [randint_stream], ShellCmd,
        'cat < IN_STREAM > OUT_STREAM',
        out_record_def=api.RecordDef([{'name': 'num', 'type': 'INT'}]),
        out_col_patterns={'num': re.compile(r'^.+$', re.MULTILINE)})
    api.OStream(cat_stream, LocalFile, OUTPUT_FILE, output_format='json', fixed_to=['localhost'])


def test():
    import json

    with open(OUTPUT_FILE) as f:
        for i, line in enumerate(f):
            record = json.loads(line)
            assert(0 <= int(record['num']) <= 100)
    assert(i + 1 == NUM_RECORDS)
