# -*- coding: utf-8 -*-
from os.path import abspath
import re
from shellstreaming import api
from shellstreaming.istream import RandSentence
from shellstreaming.operator import ShellCmd
from shellstreaming.ostream import LocalFile


OUTPUT_FILE = '/tmp/50_wordcount.txt'
NUM_RECORDS = 100000
SPLIT_SENTENCE = abspath(__file__) + '/shellcmd/split_sentence'  # input: sentence, output: words
WORD_COUNT     = abspath(__file__) + '/shellcmd/word_count'      # input: word, output: occurence count of the word


def main():
    sentence_stream = api.IStream(RandSentence, sleep_sec=1e-7, max_records=NUM_RECORDS)
    word_stream = api.Operator(
        [sentence_stream], ShellCmd,
        '%s < IN_STREAM > OUT_STREAM' % (SPLIT_SENTENCE),
        daemon=True,
        out_record_def=api.RecordDef([{'name': 'word', 'type': 'STRING'}]),
        out_col_patterns={'word': re.compile(r'^.+$', re.MULTILINE)},
        msg_to_cmd='extraordinarylongword.\n',
        reply_from_cmd='extraordinarylongword\n')

    word_stream.partition_by_key('word')

    wc_stream = api.Operator(
        [word_stream], ShellCmd,
        '%s < IN_STREAM > OUT_STREAM' % (WORD_COUNT),
        daemon=True,
        out_record_def=api.RecordDef([{'name': 'word', 'type': 'STRING'}, {'name': 'count', 'type': 'INT'}]),
        out_col_patterns={
            'word'  : re.compile(r'^.+ ', re.MULTILINE),
            'count' : re.compile(r'\d+$', re.MULTILINE),
        },
        msg_to_cmd='extraordinarylongword\n',
        reply_from_cmd='extraordinarylongword 1\n')

    api.OStream(wc_stream, LocalFile, OUTPUT_FILE, output_format='json')  # 各ワーカのログに吐かれる
