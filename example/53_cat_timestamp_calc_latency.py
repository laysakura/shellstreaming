#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
from datetime import datetime as dt
from dateutil.parser import parser


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('ARGS: BEFORE_TIMESTAMP_FILE AFTER_TIMESTAMP_FILE\n')
        sys.exit(1)

    before_fpath, after_fpath = sys.argv[1:3]

    with open(before_fpath) as before_f, open(after_fpath) as after_f:
        before_lines = before_f.readlines()
        after_lines  = after_f.readlines()

    assert(len(before_lines) == len(after_lines))

    p = parser()
    latencies_sec = []
    for i in xrange(len(before_lines)):
        before_record, after_record = (json.loads(before_lines[i]), json.loads(after_lines[i]))
        before_ts, after_ts = (p.parse(before_record['t']), p.parse(after_record['t']))
        delta = after_ts - before_ts
        latencies_sec.append(delta.seconds + delta.microseconds * 1e-6)

    print('mean latency = %f sec ; max latency = %f sec ; min latency = %f sec' %
          (sum(latencies_sec) / len(latencies_sec), max(latencies_sec), min(latencies_sec)))
