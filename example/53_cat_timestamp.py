# -*- coding: utf-8 -*-
from os.path import abspath, dirname
import re
from shellstreaming import api
from shellstreaming.istream.timestamp import Timestamp
from shellstreaming.operator import ShellCmd, CopySplit
from shellstreaming.ostream import LocalFile


BEFORE_OUTPUT_FILE = '/home/nakatani/tmp2/53_cat_timestamp_before.txt'
AFTER_OUTPUT_FILE  = '/home/nakatani/tmp2/53_cat_timestamp_after.txt'
NUM_RECORDS        = 50000
SHELLCMD_DIR       = abspath(dirname(__file__))
TIMESTAMPER        = SHELLCMD_DIR + '/shellcmd/timestamper.py'
FIXED_TO           = ['cloko020:10000']

RECORDS_IN_BATCH = 1000


def main():
    with open(BEFORE_OUTPUT_FILE, 'w'):
        pass
    with open(AFTER_OUTPUT_FILE, 'w'):
        pass

    ts_stream = api.IStream(Timestamp, sleep_sec=1e-7, max_records=NUM_RECORDS, fixed_to=FIXED_TO, records_in_batch=RECORDS_IN_BATCH)
    ts_stream0, ts_stream1 = api.Operator([ts_stream], CopySplit, 2)
    api.OStream(ts_stream0, LocalFile, BEFORE_OUTPUT_FILE, output_format='json', fixed_to=FIXED_TO)


    cat_stream = api.Operator(
        [ts_stream1], ShellCmd,
        '%s < IN_STREAM > OUT_STREAM' % (TIMESTAMPER),
        # daemon=True,
        out_record_def=api.RecordDef([{'name': 't', 'type': 'STRING'}]),
        out_col_patterns={'t': re.compile(r'^.+$', re.MULTILINE)},
        # msg_to_cmd='hello\n',
        # reply_from_cmd='hello\n'
    )

    api.OStream(cat_stream, LocalFile, AFTER_OUTPUT_FILE, output_format='json', fixed_to=FIXED_TO)


def test():
    import json
    from datetime import datetime as dt
    from dateutil.parser import parser

    p = parser()
    # before timestamper
    for path in (BEFORE_OUTPUT_FILE, AFTER_OUTPUT_FILE):
        with open(path) as f:
            prev_ts = dt(year=1900, month=1, day=1)
            for i, line in enumerate(f):
                record = json.loads(line)
                ts_str = record['t']
                ts = p.parse(ts_str)
                # print('ts_str=%s ; ts=%s', (ts_str, ts))
                ts > prev_ts
            assert(i + 1 == NUM_RECORDS)
