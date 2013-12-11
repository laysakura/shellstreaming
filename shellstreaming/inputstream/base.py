# -*- coding: utf-8 -*-
"""
    shellstreaming.inputstream.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides abstract FiniteStream and InfiniteStream.
"""
import threading
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty
from abc import ABCMeta, abstractmethod
from shellstreaming.timed_batch import TimedBatch
from shellstreaming.timespan import Timespan


class Base(threading.Thread):
    """Base class for :class:`FiniteStream` & :class:`InfiniteStream`.

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
        self._batch_q       = Queue()

        # for creating batches one by one
        self._next_batch_span = None
        self._next_batch      = None

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
        """Function for inputstream subclasses to add records fetched.

        .. warning::
            Current constraint: `record.timestamp` of formmer must be not greater than that of later one.
            i.e. asserting ``rec1.timestamp <= rec2.timestamp`` where ``add(rec1) ; add(rec2)``

            Therefore, current version does not support user-defined timestamp.

        :param record: Give `None` to signal consumer that data-fetching process has end.
        """
        # [fixme] - record.timestamp is asserted as arrival time. User defined timestamp is not supported.
        # To support it, this function may wait longer to collect records and then make multiple batchs
        # each of which has different timestamp range.

        def _when_got_last_record():
            if self._next_batch:
                _produce_next_batch()
            _no_more_batch()

        def _produce_next_batch():
            batch = TimedBatch(self._next_batch_span, tuple(self._next_batch))
            self._batch_q.put(batch)

        def _no_more_batch():
            self._batch_q.put(None)

        def _create_next_batch():
            self._next_batch      = []
            self._next_batch_span = Timespan(record.timestamp, self._batch_span_ms)

        if record is None:
            _when_got_last_record()
            return

        if self._next_batch is None:
            _create_next_batch()

        assert(not record.timestamp.runoff_lower(self._next_batch_span))

        if record.timestamp.runoff_higher(self._next_batch_span):
            # this record is for 2nd batch
            _produce_next_batch()
            _create_next_batch()

        self._next_batch.append(record)

    def __iter__(self):
        return self

    @abstractmethod
    def next(self):  # pragma: no cover
        pass

    @abstractmethod
    def run(self):  # pragma: no cover
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

        while True:
            try:
                # [todo] - return batch with oldest timestamp?
                batch = self._batch_q.get(timeout=365 * 24 * 60 * 60)  # workaround: enable Ctrl-C http://bugs.python.org/issue1360
                break
            except Empty:
                continue

        assert(batch is not None)
        return batch


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

    def next(self):
        """Return one of batches in out-of-order.

        :raises: `StopIteration` when data-fetching thread has already finished or when interrupted
        """
        if self.interrupted():
            raise StopIteration

        # [todo] - return batch with oldest timestamp?
        while True:
            try:
                # [todo] - return batch with oldest timestamp?
                batch = self._batch_q.get(timeout=365 * 24 * 60 * 60)  # workaround: enable Ctrl-C http://bugs.python.org/issue1360
                break
            except Empty:
                continue

        if batch is None:  # means producer thread has sent end signal
            raise StopIteration
        return batch
