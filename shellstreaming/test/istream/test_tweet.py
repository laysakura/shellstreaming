# -*- coding: utf-8 -*-

# This test is supposed to be ignored in `setup.cfg`

from nose.tools import *
from os.path import abspath, dirname, join, exists
from ConfigParser import SafeConfigParser
from shellstreaming.batch_queue import BatchQueue
from shellstreaming.istream.tweet import Tweet


def test_tweet_usage():
    # To fully pass this test, create 'shellstreaming/test/data/shellstreaming_test_tweet.cnf' whose contents are:
    #
    # [istream.tweet]
    # consumer_key = <your consumer key>
    # consumer_secret = <your consumer secret>
    # access_token = <your access token>
    # access_token_secret = <your access token secret>
    confpath = join(abspath(dirname(__file__)), '..', 'data', 'shellstreaming_test_tweet.cnf')
    assert_true(exists(confpath))

    config = SafeConfigParser()
    config.read(confpath)

    q         = BatchQueue()
    stream = Tweet(
        public_tweets_url='https://stream.twitter.com/1.1/statuses/sample.json',
        consumer_key=config.get('istream.tweet', 'consumer_key'),
        consumer_secret=config.get('istream.tweet', 'consumer_secret'),
        access_token=config.get('istream.tweet', 'access_token'),
        access_token_secret=config.get('istream.tweet', 'access_token_secret'),

        output_queue=q,
        batch_span_ms=1000,
    )

    n_batches = 5
    while n_batches > 0:
        batch = q.pop()
        print(batch)
        n_batches -= 1

    stream.interrupt()
    # q may have batches yet
