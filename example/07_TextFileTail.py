# -*- coding: utf-8 -*-
"""
Append text to INPUT_FILE, and then OUTPUT_FILE grows...

    $ echo 'any text' >> /tmp/07_TextFileTail-in.txt
    $ tail -f /tmp/07_TextFileTail-out.txt
"""
from shellstreaming import api
from shellstreaming.istream import TextFileTail
from shellstreaming.ostream import LocalFile


INPUT_FILE  = '/tmp/07_TextFileTail-in.txt'
OUTPUT_FILE = '/tmp/07_TextFileTail-out.txt'


def main():
    # create input file first
    with open(INPUT_FILE, 'w'):
        pass

    tail_stream = api.IStream(TextFileTail, INPUT_FILE, read_existing_lines=False, fixed_to=['localhost'])
    api.OStream(tail_stream, LocalFile, OUTPUT_FILE, output_format='json', fixed_to=['localhost'])


def test():
    pass
