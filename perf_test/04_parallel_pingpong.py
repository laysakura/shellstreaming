# -*- coding: utf-8 -*-
from shellstreaming import api
from shellstreaming.istream import IncInt
from shellstreaming.ostream import Null


NUM_RECORDS     = 1000000
RECORDS_IN_BATH = 100

## cloko[[020-035]] x 8
FIXED_TO = 'cloko020:10000,cloko021:10000,cloko022:10000,cloko023:10000,cloko024:10000,cloko025:10000,cloko026:10000,cloko027:10000,cloko028:10000,cloko029:10000,cloko030:10000,cloko031:10000,cloko032:10000,cloko033:10000,cloko034:10000,cloko035:10000,cloko020:10001,cloko021:10001,cloko022:10001,cloko023:10001,cloko024:10001,cloko025:10001,cloko026:10001,cloko027:10001,cloko028:10001,cloko029:10001,cloko030:10001,cloko031:10001,cloko032:10001,cloko033:10001,cloko034:10001,cloko035:10001,cloko020:10002,cloko021:10002,cloko022:10002,cloko023:10002,cloko024:10002,cloko025:10002,cloko026:10002,cloko027:10002,cloko028:10002,cloko029:10002,cloko030:10002,cloko031:10002,cloko032:10002,cloko033:10002,cloko034:10002,cloko035:10002,cloko020:10003,cloko021:10003,cloko022:10003,cloko023:10003,cloko024:10003,cloko025:10003,cloko026:10003,cloko027:10003,cloko028:10003,cloko029:10003,cloko030:10003,cloko031:10003,cloko032:10003,cloko033:10003,cloko034:10003,cloko035:10003,cloko020:10004,cloko021:10004,cloko022:10004,cloko023:10004,cloko024:10004,cloko025:10004,cloko026:10004,cloko027:10004,cloko028:10004,cloko029:10004,cloko030:10004,cloko031:10004,cloko032:10004,cloko033:10004,cloko034:10004,cloko035:10004,cloko020:10005,cloko021:10005,cloko022:10005,cloko023:10005,cloko024:10005,cloko025:10005,cloko026:10005,cloko027:10005,cloko028:10005,cloko029:10005,cloko030:10005,cloko031:10005,cloko032:10005,cloko033:10005,cloko034:10005,cloko035:10005,cloko020:10006,cloko021:10006,cloko022:10006,cloko023:10006,cloko024:10006,cloko025:10006,cloko026:10006,cloko027:10006,cloko028:10006,cloko029:10006,cloko030:10006,cloko031:10006,cloko032:10006,cloko033:10006,cloko034:10006,cloko035:10006,cloko020:10007,cloko021:10007,cloko022:10007,cloko023:10007,cloko024:10007,cloko025:10007,cloko026:10007,cloko027:10007,cloko028:10007,cloko029:10007,cloko030:10007,cloko031:10007,cloko032:10007,cloko033:10007,cloko034:10007,cloko035:10007'.split(',')

## cloko[[020-035]]
# FIXED_TO = 'cloko020:10000,cloko021:10000,cloko022:10000,cloko023:10000,cloko024:10000,cloko025:10000,cloko026:10000,cloko027:10000,cloko028:10000,cloko029:10000,cloko030:10000,cloko031:10000,cloko032:10000,cloko033:10000,cloko034:10000,cloko035:10000'.split(',')

## cloko[[020-027]]
# FIXED_TO = 'cloko020:10000,cloko021:10000,cloko022:10000,cloko023:10000,cloko024:10000,cloko025:10000,cloko026:10000,cloko027:10000'.split(',')

## cloko[[020-023]]
# FIXED_TO = 'cloko020:10000,cloko021:10000,cloko022:10000,cloko023:10000'.split(',')

## cloko[[020-021]]
# FIXED_TO = 'cloko020:10000,cloko021:10000'.split(',')

## cloko[[020]]
# FIXED_TO = 'cloko020:10000'.split(',')


def main():
    randint_stream = api.IStream(IncInt, sleep_sec=None, max_records=NUM_RECORDS,
                                 records_in_batch=RECORDS_IN_BATH,
                                 fixed_to=FIXED_TO)
    api.OStream(randint_stream, Null,
                fixed_to=FIXED_TO)
