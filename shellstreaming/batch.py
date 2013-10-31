# -*- coding: utf-8 -*-
"""
    shellstreaming.batch
    ~~~~~~~~~~~~~~~~~~~~

    Set of records assembled by timestamp.

    From users' perspective, `Batch` is equivalent to so-called `window` in stream processing's context.
    Also, a `Batch` is passed to an operator at-a-time internally.
"""
from Queue import Queue
from shellstreaming.error import TimestampError


class Batch(object):
    """Set of records assembled by timestamp"""
    def __init__(self, timespan, record_q, timestamp_check=False):
        """Create an *immutable* batch of records

        :param timespan: timespan of this batch
        :param record_q: Records. *Last element must be `None`*.
        :type record_q:  instance of `Queue.Queue`
        :param timestamp_check: if `True`, checks timestamp of each record is between `[timestamps_start, timestamps_end)`
        :raises: TimestampError when at least one of record's timestamp exceeds `[timestamps_start, timestamps_end)`
        """
        assert(isinstance(record_q, Queue))

        self.timespan  = timespan
        self._record_q = record_q

        if timestamp_check:
            Batch._chk_timestamp(self._ts_start, self._ts_end, self._records)

    def __iter__(self):
        return self

    def next(self):
        """Return one of record in this batch in out-of-order.

        :raises: `StopIteration` when no more record is in this batch
        """
        # TODO: return record with oldest timestamp? => possible if using Queue.PriorityQueue
        # print('getting record...')
        record = self._record_q.get()
        # print('got record: %s' % (record))
        if record is None:
            raise StopIteration
        return record
