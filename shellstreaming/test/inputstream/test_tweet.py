# -*- coding: utf-8 -*-
from nose.tools import *
from os.path import abspath, dirname, join
from shellstreaming.config import Config
from shellstreaming.inputstream.tweet import Tweet


config = None


def setup():
    global config
    confpath = join(abspath(dirname(__file__)), '..', 'data', 'shellstreaming_test_tweet.cnf')
    config = Config.instance()
    config.set_config_file(confpath)


def test_tweet_usage():
    global config
    n_batches = 2
    stream = Tweet(
        # [todo] - use config for not showing my keys & secrets
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
