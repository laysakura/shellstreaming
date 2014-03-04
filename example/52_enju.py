# -*- coding: utf-8 -*-
from os.path import abspath, dirname
import re
from shellstreaming import api
from shellstreaming.istream import RandSentence
from shellstreaming.operator import ShellCmd
from shellstreaming.ostream import Null, LocalFile


OUTPUT_FILE    = '/tmp/52_enju.txt'
NUM_RECORDS    = 100
RECORDS_IN_BATCH = 10
SHELLCMD_DIR   = abspath(dirname(__file__))
ENJU           = '/home/nakatani/svn/workflows/apps/event_recog/modules/tools/enju-install/enju'

## cloko[[020-035]]
FIXED_TO = 'cloko020:10000,cloko021:10000,cloko022:10000,cloko023:10000,cloko024:10000,cloko025:10000,cloko026:10000,cloko027:10000,cloko028:10000,cloko029:10000,cloko030:10000,cloko031:10000,cloko032:10000,cloko033:10000,cloko034:10000,cloko035:10000'.split(',')

## cloko[[020-027]]
#FIXED_TO = 'cloko020:10000,cloko021:10000,cloko022:10000,cloko023:10000,cloko024:10000,cloko025:10000,cloko026:10000,cloko027:10000'.split(',')

## cloko[[020-023]]
#FIXED_TO = 'cloko020:10000,cloko021:10000,cloko022:10000,cloko023:10000'.split(',')

## cloko[[020-021]]
#FIXED_TO = 'cloko020:10000,cloko021:10000'.split(',')

## cloko[[020]]
#FIXED_TO = 'cloko020:10000'.split(',')


def main():
    with open(OUTPUT_FILE, 'w'):
        pass

    sentence_stream = api.IStream(RandSentence, seed=1, sleep_sec=1e-7, max_records=NUM_RECORDS,
                                  records_in_batch=RECORDS_IN_BATCH, fixed_to=FIXED_TO)
    enju_stream = api.Operator(
        [sentence_stream], ShellCmd,
        '%s < IN_STREAM > OUT_STREAM' % (ENJU),
        daemon=True,
        out_record_def=api.RecordDef([{'name': 'enju', 'type': 'STRING'}]),
        out_col_patterns={'enju': re.compile(r'.+?\n\n', re.DOTALL)},
        msg_to_cmd='\n',
        reply_from_cmd='Empty line\n'
    )

    api.OStream(enju_stream, Null, fixed_to=FIXED_TO)
    # api.OStream(enju_stream, LocalFile, OUTPUT_FILE, output_format='json', fixed_to=FIXED_TO)
