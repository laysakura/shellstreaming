# -*- coding: utf-8 -*-
"""
    shellstreaming.inputstream.tweet
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Generates public tweets sequence.
"""
import json
import requests
from requests_oauthlib import OAuth1
from shellstreaming.inputstream.base import InfiniteStream
from shellstreaming.config import Config
from shellstreaming.record import Record
from shellstreaming.recorddef import RecordDef


class Tweet(InfiniteStream):
    """Infinite input stream which generates public tweets sequence.

    .. note::
        Not every attribute is fetched from API.
        See `Tweets <https://dev.twitter.com/docs/platform-objects/tweets>`_ for further attributes to analyze.
    """
    def __init__(
        self,
        consumer_key, consumer_secret,
        access_token, access_token_secret,

        batch_span_ms=1000,
    ):
        """Constructor

        :raises: :class:`requests.HTTPError` if twitter API returns error response status
        """
        self._twitter_response = Tweet._get_twitter_streaming_response(
            consumer_key, consumer_secret, access_token, access_token_secret)
        InfiniteStream.__init__(self, batch_span_ms)

    def run(self):
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
            if line == '':
                continue
            line_dict = json.loads(line)
            if 'text' in line_dict:  # [fix] - wired condition...
                (text, lang, created_at, screen_name) = (
                    line_dict['text'], line_dict['lang'], line_dict['created_at'], line_dict['user']['screen_name'])
                self.add(Record(
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
