# -*- coding: utf-8 -*-

# This test is supposed to be ignored in `setup.cfg`

from nose.tools import *
from os.path import abspath, dirname, join, exists
from ConfigParser import SafeConfigParser
from shellstreaming.inputstream.tweet import Tweet


def test_tweet_usage():
    # To fully pass this test, create 'shellstreaming/test/data/shellstreaming_test_tweet.cnf' whose contents are:
    #
    # [inputstream.tweet]
    # consumer_key = <your consumer key>
    # consumer_secret = <your consumer secret>
    # access_token = <your access token>
    # access_token_secret = <your access token secret>
    confpath = join(abspath(dirname(__file__)), '..', 'data', 'shellstreaming_test_tweet.cnf')
    assert_true(exists(confpath))

    config = SafeConfigParser()
    config.read(confpath)

    n_batches = 5
    stream = Tweet(
        public_tweets_url='https://stream.twitter.com/1.1/statuses/sample.json',
        consumer_key=config.get('inputstream.tweet', 'consumer_key'),
        consumer_secret=config.get('inputstream.tweet', 'consumer_secret'),
        access_token=config.get('inputstream.tweet', 'access_token'),
        access_token_secret=config.get('inputstream.tweet', 'access_token_secret'),

        batch_span_ms=1000,
    )
    for i_batch, batch in enumerate(stream):
        print(batch)
        n_batches -= 1
        if n_batches == 0:
            stream.interrupt()
