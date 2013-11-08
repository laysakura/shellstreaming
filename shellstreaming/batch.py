# -*- coding: utf-8 -*-
"""
    shellstreaming.batch
    ~~~~~~~~~~~~~~~~~~~~

    :synopsis: Set of records assembled by timestamp.

    From users' perspective, `Batch` is equivalent to so-called `window` in stream processing's context.
    Also, a `Batch` is passed to an operator at-a-time internally.
"""
try:
    from Queue import Queue
except ImportError:
    from queue import Queue
from shellstreaming.error import TimestampError


class Batch(object):
    """Set of records assembled by timestamp"""
    def __init__(self, timespan, record_q, timestamp_check=False):
        """Create an *immutable* batch of records

        :param timespan: timespan of this batch
        :param record_q: records
        :type record_q:  instance of `Queue.Queue`
        :param timestamp_check: if `True`, checks timestamp of each record is between `[timestamps_start, timestamps_end)`
        :raises: TimestampError when at least one of record's timestamp exceeds `[timestamps_start, timestamps_end)`
        """
        assert(isinstance(record_q, Queue))

        self.timespan  = timespan
        self._record_q = record_q
        self._record_q.put(None)  # last element must be `None`

        if timestamp_check:
            Batch._chk_timestamp(self.timespan, self._record_q)

    def __iter__(self):
        return self

    def next(self):
        """Return one of record in this batch in out-of-order.

        :raises: `StopIteration` when no more record is in this batch
        """
        # TODO: return record with oldest timestamp? => possible if using Queue.PriorityQueue
        record = self._record_q.get()
        if record is None:
            raise StopIteration
        return record

    # private functions
    @staticmethod
    def _chk_timestamp(timespan, record_q):
        """Check if all records in `record_q` has timestamp between `timespan`

        :raises: `TimestampError` if check failed
        """
        while True:
            rec = record_q.get()
            record_q.put(rec)
            if rec is None:
                return
            if not rec.timestamp.between(timespan):
                raise TimestampError('Following record\'s timestamp is %s, which runs off %s: \n%s' %
                                     (rec.timestamp, timespan, rec))
