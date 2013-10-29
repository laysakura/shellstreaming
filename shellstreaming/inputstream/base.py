# -*- coding: utf-8 -*-
"""
    shellstreaming.inputstream.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import threading
from shellstreaming.batch import Batch
from shellstreaming.batch_set import BatchSet


class Base(threading.Thread):
    def __init__(self, batch_span_ms):
        self._batch_span_ms = batch_span_ms
        self._batches       = BatchSet()

        # threading
        threading.Thread.__init__(self)
        self.daemon     = True               # to die when master process dies
        self._interrupt = threading.Event()  # to become ready to die when `interrupt()` is called
        self.start()

    def interrupt(self):
        self._interrupt.set()

    def interrupted(self):
        return self._interrupt.is_set()

    def add(self, record):
        ts = record.timestamp
        batch = self._batches.find_batch(timestamp=ts)  # batch : Batch obj (Batch is also thread-safe queue?)
        if batch is None:
            batch = Batch(timestamp_start=ts, timestamp_end=ts + self._batch_span_ms)
            self._batches.add(batch)
        batch.add(record)

    def __iter__(self):
        return self


class InfiniteStream(Base):
    def __init__(self, batch_span_ms):
        Base.__init__(self, batch_span_ms)

    def next(self):
        # TODO: return batch with oldest timestamp?
        return self._batches.pop()


class FiniteStream(Base):
    def __init__(self, batch_span_ms):
        self._fetch_finished = False
        Base.__init__(self, batch_span_ms)

    def finish_fetching(self):
        self._fetch_finished = True

    def fetch_finished(self):
        return self._fetch_finished

    def no_more_input(self):
        return self.fetch_finished() and len(self._batches)

    def next(self):
        if self.no_more_input():
            raise StopIteration
        # TODO: return batch with oldest timestamp?
        return self._batches.pop()
