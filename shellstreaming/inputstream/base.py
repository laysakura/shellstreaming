# -*- coding: utf-8 -*-
"""
    shellstreaming.inputstream.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides abstract FiniteStream and InfiniteStream.
"""
import threading
from abc import ABCMeta, abstractmethod
from shellstreaming.batch import Batch
from shellstreaming.batch_set import BatchSet


class Base(threading.Thread):
    """Base class for FiniteStream & InfiniteStream.

    .. warning::
        Do not create direct subclasses of `Base <#shellstreaming.inputstream.base.Base>`_ .
        Use `FiniteStream <#shellstreaming.inputstream.base.FiniteStream>`_ or
        `InfiniteStream <#shellstreaming.inputstream.base.InfiniteStream>`_ instead.

    An inputstream class must have `run()` method, which runs as a thread to fetch input data from outside.
    """
    __metaclass__ = ABCMeta

    def __init__(self, batch_span_ms):
        """Constructor

        :param batch_span_ms: timespan to assemble records as batch
        """
        self._batch_span_ms = batch_span_ms
        self._batches       = BatchSet()

        # threading
        threading.Thread.__init__(self)
        self.daemon     = True               # to die when master process dies
        self._interrupt = threading.Event()  # to become ready to die when `interrupt()` is called
        self.start()

    def interrupt(self):
        """API to safely kill data-fetching thread.

        *Example:*

        .. code-block:: python

            n_input = 5
            stream = Stdin(batch_span_ms=1000)
            for batch in stream:
                if batch is None:
                    time.sleep(5)
                    continue
            
                for record in batch:
                    print(record)
            
                n_input -= len(batch)
                if n_input <= 0:
                    stream.interrupt()  # kill thread fetching data from stdin

        When interrupted, each inputstream subclass must finish data-fetching thread with necessary destruction processes.

        .. code-block:: python

            class Stdin(InfiniteStream):
                def __init__(self, batch_span_ms=1000):
                    Base.__init__(self, batch_span_ms)
            
                def run(self):
                    rdef = [{'name': 'line', 'type': 'STRING'}]
                    while True:
                        if self.interrupted():  # probes interruption
                            break
                        try:
                            line = raw_input().rstrip('\\r\\n')
                            self.add(Record(rdef, line))
                        except EOFError as e:
                            continue
            
                    # HERE COMES DESTRUCTION PROCESSES (like `close` etc...)
        """
        self._interrupt.set()

    def interrupted(self):
        """Function for inputstream subclasses to probe interruption"""
        return self._interrupt.is_set()

    def add(self, record):
        """Function for inputstream subclasses to add records fetched"""
        ts = record.timestamp
        batch = self._batches.find_batch(timestamp=ts)  # batch : Batch obj (Batch is also thread-safe queue?)
        if batch is None:
            batch = Batch(timestamp_start=ts, timestamp_end=ts + self._batch_span_ms)
            self._batches.add(batch)
        batch.add(record)

    def __iter__(self):
        return self

    @abstractmethod
    def next(self):
        pass

    @abstractmethod
    def run(self):
        pass


class InfiniteStream(Base):
    """Base class for any InfiniteStreams, which stops data-fetching thread only when interrupted."""
    __metaclass__ = ABCMeta

    def __init__(self, batch_span_ms):
        """Constructor

        :param batch_span_ms: timespan to assemble records as batch
        """
        Base.__init__(self, batch_span_ms)

    def next(self):
        """Return one of batches in out-of-order

        :raises: `StopIteration` only when interrupted
        """
        if self.interrupted():
            raise StopIteration
        # TODO: return batch with oldest timestamp?
        return self._batches.pop()


class FiniteStream(Base):
    """Base class for any FiniteStreams, which stops data-fetching thread after all data are fetched or when interrupted.

    `run()` method of any subclass must call `finish_fetching() <#shellstreaming.inputstream.base.FiniteStream.finish_fetching>`_
    method after all data are fetched.

    *Example:*

    .. code-block:: python

        class TextFile(FiniteStream):
            def __init__(self, path, batch_span_ms=1000):
                self._path = path
                FiniteStream.__init__(self, batch_span_ms)
        
            def run(self):
                with open(self._path) as f:
                    rdef = [{'name': 'line', 'type': 'STRING'}]
                    line = f.readline()
                    while line:
                        self.add(Record(rdef, line))
                        line = f.readline()
                self.finish_fetching()  # to notify user data-fetching thread has finished
    """
    def __init__(self, batch_span_ms):
        """Constructor

        :param batch_span_ms: timespan to assemble records as batch
        """
        self._fetch_finished = False
        Base.__init__(self, batch_span_ms)

    def finish_fetching(self):
        """Function FiniteStream's subclasses must call after finishing data fetching"""
        self._fetch_finished = True

    def next(self):
        """Return one of batches in out-of-order

        :raises: `StopIteration` when data-fetching thread has already finished or when interrupted
        """
        if self.interrupted() or self._no_more_input():
            raise StopIteration
        # TODO: return batch with oldest timestamp?
        return self._batches.pop()

    # private functions
    def _no_more_input(self):
        return self._fetch_finished and len(self._batches) == 0
