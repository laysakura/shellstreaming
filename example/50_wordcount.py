# -*- coding: utf-8 -*-
from os.path import abspath, dirname
import re
from shellstreaming import api
from shellstreaming.istream import RandSentence
from shellstreaming.operator import ShellCmd
from shellstreaming.ostream import LocalFile


OUTPUT_FILE    = '/tmp/50_wordcount.txt'
NUM_RECORDS    = 10000
SHELLCMD_DIR   = abspath(dirname(__file__))
SPLIT_SENTENCE = SHELLCMD_DIR + '/shellcmd/split_sentence'  # input: sentence, output: words
WORD_COUNT     = SHELLCMD_DIR + '/shellcmd/word_count'      # input: word, output: occurence count of the word


def main():
    sentence_stream = api.IStream(RandSentence, seed=1, sleep_sec=1e-7, max_records=NUM_RECORDS, fixed_to=['localhost'])
    word_stream = api.Operator(
        [sentence_stream], ShellCmd,
        '%s < IN_STREAM > OUT_STREAM' % (SPLIT_SENTENCE),
        daemon=True,
        out_record_def=api.RecordDef([{'name': 'word', 'type': 'STRING'}]),
        out_col_patterns={'word': re.compile(r'^.+$', re.MULTILINE)},
        msg_to_cmd='extraordinarylongword\n',
        reply_from_cmd='extraordinarylongword\n')

    word_stream.partition_by_key('word')

    wc_stream = api.Operator(
        [word_stream], ShellCmd,
        '%s < IN_STREAM > OUT_STREAM' % (WORD_COUNT),
        daemon=True,
        migratable=False,
        out_record_def=api.RecordDef([{'name': 'word', 'type': 'STRING'}, {'name': 'count', 'type': 'INT'}]),
        out_col_patterns={
            'word'  : re.compile(r'^.+(?= )', re.MULTILINE),
            'count' : re.compile(r'\d+$', re.MULTILINE),
        },
        msg_to_cmd='not word\n',
        reply_from_cmd='single word is expected\n'
    )

    api.OStream(wc_stream, LocalFile, OUTPUT_FILE, output_format='json', fixed_to=['localhost'])


# def test():
#     import json

#     with open(OUTPUT_FILE) as f:
#         for i, line in enumerate(f):
#             record = json.loads(line)
#             assert(0 <= int(record['num']) <= 100)
#     assert(i + 1 == NUM_RECORDS)
