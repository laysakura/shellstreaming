# -*- coding: utf-8 -*-
from os.path import join, abspath, dirname
import re
from shellstreaming import api
from shellstreaming.istream import TextFileTail
from shellstreaming.operator import ShellCmd, ExternalTimeWindow, CopySplit
from shellstreaming.ostream import LocalFile


APACHE_LOG   = '/tmp/access.log'
DAILY_ACCESS = '/tmp/51_apache_log_analysis_daily.txt'
STATUS_CODES = '/tmp/51_apache_log_analysis_statuscode.txt'

workers_with_access_log   = ['cloko020:10000', 'cloko021:10000']
worker_to_collect_results = ['cloko022:10000']


def main():
    log_stream = api.IStream(TextFileTail, APACHE_LOG, read_existing_lines=True,
                             fixed_to=workers_with_access_log)

    # filter lines in which '/' is 'GET' accessed
    access_stream = api.Operator(
        [log_stream], ShellCmd,
        r'''grep -E '"GET / HTTP/[.0-9]+"' < IN_STREAM > OUT_STREAM''',
        success_exitcodes=(0, 1),
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
        size_days=4, latest_timestamp=api.Timestamp('2014-01-04 23:59:59'),
        fixed_to=worker_to_collect_results)  # ステートフル．4日間のレコード集合という状態を持つ

    # copy 2 way
    access_win0, access_win1 = api.Operator([access_win], CopySplit, 2)

    ########################################
    # path 1: group by date
    ########################################

    # projection: get timestamp column & retrieve date
    date_win = api.Operator(
        [access_win0], ShellCmd,
        r'''awk '{print $2}' < IN_STREAM > OUT_STREAM''',
        out_record_def=api.RecordDef([{'name': 'date', 'type': 'STRING'}]),
        out_col_patterns={'date': re.compile(r'^.+$', re.MULTILINE)})

    # sort date for `uniq -c` command
    sorted_date_win = api.Operator(
        [date_win], ShellCmd,
        r'''sort < IN_STREAM > OUT_STREAM''',
        out_record_def=api.RecordDef([{'name': 'date', 'type': 'STRING'}]),
        out_col_patterns={'date': re.compile(r'^.+$', re.MULTILINE)})

    # group by date
    count_group_by_date = api.Operator(
        [sorted_date_win], ShellCmd,
        r'''uniq -c < IN_STREAM > OUT_STREAM''',
        out_record_def=api.RecordDef([
            {'name': 'count' , 'type': 'INT'},
            {'name': 'date'  , 'type': 'STRING'},
        ]),
        out_col_patterns={
            'count': re.compile(r'\d+', re.MULTILINE),
            'date': re.compile(r'\d{4}-\d{2}-\d{2}', re.MULTILINE),
        })

    api.OStream(count_group_by_date, LocalFile, DAILY_ACCESS, output_format='json', fixed_to=worker_to_collect_results)

    ########################################
    # path 2: group by status code
    ########################################

    # projection: get status code
    statuscode_win = api.Operator(
        [access_win1], ShellCmd,
        r'''awk -F "|" '{print $3}' < IN_STREAM > OUT_STREAM''',
        in_column_sep='|',
        out_record_def=api.RecordDef([{'name': 'statuscode', 'type': 'INT'}]),
        out_col_patterns={'statuscode': re.compile(r'^.+$', re.MULTILINE)})

    # sort date for `uniq -c` command
    sorted_statuscode_win = api.Operator(
        [statuscode_win], ShellCmd,
        r'''sort < IN_STREAM > OUT_STREAM''',
        out_record_def=api.RecordDef([{'name': 'statuscode', 'type': 'INT'}]),
        out_col_patterns={'statuscode': re.compile(r'^.+$', re.MULTILINE)})

    # group by date
    count_group_by_statuscode = api.Operator(
        [sorted_statuscode_win], ShellCmd,
        r'''uniq -c < IN_STREAM > OUT_STREAM''',
        out_record_def=api.RecordDef([
            {'name': 'count'     , 'type': 'INT'},
            {'name': 'statuscode', 'type': 'INT'},
        ]),
        out_col_patterns={
            'count'      : re.compile(r'\d+', re.MULTILINE),
            'statuscode' : re.compile(r'\d{3}', re.MULTILINE),
        },
    fixed_to=worker_to_collect_results)

    api.OStream(count_group_by_statuscode, LocalFile, STATUS_CODES, output_format='json', fixed_to=worker_to_collect_results)


def test():
    # check DAILY_ACCESS & STATUS_CODES files.
    # also, do `$ echo 151.217.31.218 - - [04/01/2014:16:09:00 +0900] \"GET / HTTP/1.1\" 500 265 - -` and check again
    pass
