# -*- coding: utf-8 -*-
import re
from shellstreaming import api
from shellstreaming.istream import TextFileTail, TextFile
from shellstreaming.operator import ShellCmd, ExternalTimeWindow
from shellstreaming.ostream import LocalFile


APACHE_LOG     = '/home/nakatani/git/shellstreaming/example/access.log'
OUTPUT_FILE    = '/tmp/51_apache_log_analysis.txt'


def main():
    # log_stream = api.IStream(TextFileTail, APACHE_LOG,
    #                          read_existing_lines=True,
    #                          # sleep_sec=1.0,
    #                          fixed_to=['localhost'])  # webサーバが立ってるところを指定
    log_stream = api.IStream(TextFile, APACHE_LOG,
                             fixed_to=['localhost'])  # webサーバが立ってるところを指定

    # filter lines in which '/' is 'GET' accessed
    access_stream = api.Operator(
        [log_stream], ShellCmd,
        r'''grep -E "GET / HTTP/[.0-9]+" < IN_STREAM > OUT_STREAM''',
        out_record_def=api.RecordDef([
            {'name': 'ipaddr'     , 'type': 'STRING'},
            {'name': 'timestamp'  , 'type': 'STRING'},
            {'name': 'statuscode' , 'type': 'INT'},
        ]),
        out_col_patterns={
            'ipaddr'     : re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', re.MULTILINE),
            'timestamp'  : re.compile(r'(?<= - - \[).+(?=\] )', re.MULTILINE),
            'statuscode' : re.compile(r'[0-9]{3}', re.MULTILINE),
        },
    )

    # change format of timestamp to fit shellstreaming's Timestamp format
    ts_access_stream = api.Operator(
        [access_stream], ShellCmd,
        (
            r'''sed -e 's/'''
            r'''^\\([0-9]*\\.[0-9]*\\.[0-9]*\\.[0-9]*\\)|'''  # ip address (\1)
            r'''\\([0-9]*\\)\\/\\([0-9]*\\)\\/\\([0-9]*\\):\\([0-9]*\\):\\([0-9]*\\):\\([0-9]*\\).*|'''  # date (\2), month (\3), year (\4), hour (\5), minute (\6), second (\7)
            r'''\\([0-9]*\\)'''  # status code (\8)
            r'''.*$'''
            r'''/beg-ipaddr \\1 end-ipaddr beg-timestamp \\4-\\3-\\2 \\5:\\6:\\7 end-timestamp beg-statuscode \\8 end-statuscode/g' '''
            r'''< IN_STREAM > OUT_STREAM'''
        ),
        in_column_sep='|',
        out_record_def=api.RecordDef([
            {'name': 'ipaddr'     , 'type': 'STRING'},
            {'name': 'timestamp'  , 'type': 'TIMESTAMP'},
            {'name': 'statuscode' , 'type': 'INT'},
        ]),
        out_col_patterns={
            'ipaddr'     : re.compile(r'(?<=beg-ipaddr ).+(?= end-ipaddr)', re.MULTILINE),
            'timestamp'  : re.compile(r'(?<=beg-timestamp ).+(?= end-timestamp)', re.MULTILINE),
            'statuscode' : re.compile(r'(?<=beg-statuscode ).+(?= end-statuscode)', re.MULTILINE),
        },
    )

    # make window within 2014/01/01 - 2014/01/04
    access_win = api.Operator(
        [ts_access_stream], ExternalTimeWindow,
        timestamp_column='timestamp',
        size_days=4, latest_timestamp=api.Timestamp('2014-01-04 23:59:59'))

    api.OStream(access_win, LocalFile, OUTPUT_FILE, output_format='json', fixed_to=['localhost'])


def test():
    pass
