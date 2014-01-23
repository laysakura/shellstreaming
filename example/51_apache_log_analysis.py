# -*- coding: utf-8 -*-
from os.path import join, abspath, dirname
import re
from shellstreaming import api
from shellstreaming.istream import TextFileTail
from shellstreaming.operator import ShellCmd, ExternalTimeWindow
from shellstreaming.ostream import LocalFile


APACHE_LOG   = join(abspath(dirname(__file__)), '51_apache_log_analysis_access.log')
DAILY_ACCESS = '/tmp/51_apache_log_analysis_daily.txt'
STATUS_CODES = '/tmp/51_apache_log_analysis_statuscode.txt'


def main():
    log_stream = api.IStream(TextFileTail, APACHE_LOG, read_existing_lines=True,
                             fixed_to=['localhost'])  # specify nodes where apache log exists

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
        size_days=4, latest_timestamp=api.Timestamp('2014-01-04 23:59:59'))

    # こっからコピーして分岐

    # projection: get timestamp column & retrieve date
    date_win = api.Operator(
        [access_win], ShellCmd,
        r'''awk '{print $2}' < IN_STREAM > OUT_STREAM''',
        out_record_def=api.RecordDef([{'name': 'date'  , 'type': 'STRING'}]),
        out_col_patterns={'date': re.compile(r'^.+$', re.MULTILINE)})

    # sort date for `uniq -c` command
    sorted_date_win = api.Operator(
        [date_win], ShellCmd,
        r'''sort < IN_STREAM > OUT_STREAM''',
        out_record_def=api.RecordDef([{'name': 'date'  , 'type': 'STRING'}]),
        out_col_patterns={'date': re.compile(r'^.+$', re.MULTILINE)})

    # group by date
    count_group_by_date = api.Operator(
        [sorted_date_win], ShellCmd,
        r'''uniq -c < IN_STREAM > OUT_STREAM''',
        out_record_def=api.RecordDef([
            {'name': 'count'  , 'type': 'INT'},
            {'name': 'date'  , 'type': 'STRING'},
        ]),
        out_col_patterns={
            'count': re.compile(r'\d+', re.MULTILINE),
            'date': re.compile(r'\d{4}-\d{2}-\d{2}', re.MULTILINE),
        })

    api.OStream(count_group_by_date, LocalFile, DAILY_ACCESS, output_format='json', fixed_to=['localhost'])


def test():
    pass
