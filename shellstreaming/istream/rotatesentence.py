# -*- coding: utf-8 -*-
"""
    shellstreaming.istream.randsentence
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Generates random sentence sequence.
"""
# standard modules
import time

# my modules
from relshell.record import Record
from relshell.recorddef import RecordDef
from shellstreaming.istream.base import Base


sentences = '''
(1) i am from tokyo.
(2) she is from india.
(3) my name is John.
'''.split('.')
"""Sentences come from Wikipedia's 'Beer' articld article http://en.wikipedia.org/wiki/Beer"""


class RotateSentence(Base):
    """Infinite input stream which generates random integer sequence"""
    def __init__(self, seed=None, sleep_sec=1e-3, records_in_batch=1000, **kw):
        """Constructor
        """
        self._sleep_sec     = sleep_sec
        self._len_sentences = len(sentences)
        self._cur_sentence  = 0
        Base.__init__(self, records_in_batch=records_in_batch, **kw)

    def run(self):
        rdef = RecordDef([{'name': 'sentence', 'type': 'STRING'}])
        while True:
            time.sleep(self._sleep_sec)
            if self._interrupted():
                break
            sentence = sentences[self._cur_sentence].strip().replace('\n', ' ').replace('\r', ' ').lower()
            self._cur_sentence = (self._cur_sentence + 1) % self._len_sentences
            self.add(rdef, Record(sentence))
