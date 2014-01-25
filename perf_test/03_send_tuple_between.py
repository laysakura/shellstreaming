# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import RandInt
from shellstreaming.ostream import Null


NUM_RECORDS      = 500000


def main():
    randint_stream = api.IStream(RandInt, 0, 100, sleep_sec=1e-7, max_records=NUM_RECORDS, fixed_to=['localhost'],
                                 records_in_batch=NUM_RECORDS / 1000)
    # api.OStream(randint_stream, Null, fixed_to=['localhost'])        # intra-worker tuple transfer
    api.OStream(randint_stream, Null, fixed_to=['localhost:10000'])  # inter-worker tuple transfer
