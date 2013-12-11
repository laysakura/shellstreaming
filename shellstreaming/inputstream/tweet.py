# -*- coding: utf-8 -*-
"""
    shellstreaming.inputstream.tweet
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Generates public tweets sequence.
"""
import json
import requests
from requests_oauthlib import OAuth1
from relshell.recorddef import RecordDef
from shellstreaming.inputstream.base import InfiniteStream
from shellstreaming.config import Config
from shellstreaming.timed_record import TimedRecord


class Tweet(InfiniteStream):
    """Infinite input stream which generates public tweets sequence.

    .. note::
        Not every attribute is fetched from API.
        You need to fix :class:`Tweet` to add other attributes, or develop another `inputstream`.
        See `Tweets <https://dev.twitter.com/docs/platform-objects/tweets>`_ for further attributes.
    """
    def __init__(
        self,
        consumer_key, consumer_secret,
        access_token, access_token_secret,

        batch_span_ms=1000,
    ):
        """Constructor

        :param consumer_key:        Twitter app consumer key (got from twitter)
        :param consumer_secret:     Twitter app consumer secret (got from twitter)
        :param access_token:        Twitter app access token (got from twitter)
        :param access_token_secret: Twitter app access token secret (got from twitter)
        :raises: :class:`requests.HTTPError` if twitter API returns error response status
        """
        self._twitter_response = Tweet._get_twitter_streaming_response(
            consumer_key, consumer_secret, access_token, access_token_secret)
        InfiniteStream.__init__(self, batch_span_ms)

    def run(self):
        """Fetches tweets from Twitter public stream"""
        # [todo] - support more attributes from Twitter response (https://dev.twitter.com/docs/platform-objects/tweets)
        rdef = RecordDef([
            {'name': 'text'        , 'type': 'STRING'},
            {'name': 'lang'        , 'type': 'STRING'},
            {'name': 'created_at'  , 'type': 'STRING'},  # [fix] - use timestamp type?
            {'name': 'screen_name' , 'type': 'STRING'},  # [fix] - invalid column name creates a non-killable thread (e.g. 'name': 'user.screen_name')
        ])
        for line in self._twitter_response.iter_lines():
            if self.interrupted():
                break
            line_dict = json.loads(line)
            if 'text' in line_dict:  # [fix] - wired condition...
                (text, lang, created_at, screen_name) = (
                    line_dict['text'], line_dict['lang'], line_dict['created_at'], line_dict['user']['screen_name'])
                self.add(TimedRecord(
                    rdef,
                    text.encode('utf-8') if type(text) == unicode else text,
                    lang.encode('utf-8') if type(text) == unicode else lang,
                    created_at.encode('utf-8') if type(text) == unicode else created_at,
                    screen_name.encode('utf-8') if type(text) == unicode else screen_name,
                ))

    @staticmethod
    def _get_twitter_streaming_response(
            consumer_key, consumer_secret,
            access_token, access_token_secret
    ):
        auth = OAuth1(consumer_key, consumer_secret,
                      access_token, access_token_secret,
                      signature_type='query')
        res  = requests.get(
            Config.instance().get('inputstream.tweet', 'public_tweets_url'),
            auth=auth, stream=True)
        res.raise_for_status()
        return res
