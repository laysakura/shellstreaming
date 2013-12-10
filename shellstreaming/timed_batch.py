# -*- coding: utf-8 -*-
"""
    shellstreaming.timed_batch
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Set of records assembled by timestamp.

    From users' perspective, :class:`TimedBatch` is equivalent to so-called `window` in stream processing's context.
    Also, a `Batch` is passed to an operator at-a-time internally.
"""
from relshell.batch import Batch
from shellstreaming.error import TimestampError


class TimedBatch(Batch):
    """Set of records assembled by timestamp"""
    def __init__(self, timespan, records, timestamp_check=False):
        """Create an *immutable* batch of records

        :param timespan: timespan of this batch
        :param records:  records
        :type record:    instance of `tuple`
        :param timestamp_check: if `True`, checks timestamp of each record is between `[timestamps_start, timestamps_end)`
        :raises: TimestampError when at least one of record's timestamp exceeds `[timestamps_start, timestamps_end)`
        """
        Batch.__init__(self, records)

        self.timespan = timespan
        if timestamp_check:
            TimedBatch._chk_timestamp(self.timespan, self._records)

    # private functions
    @staticmethod
    def _chk_timestamp(timespan, records):
        """Check if all records in `records` has timestamp between `timespan`

        :raises: `TimestampError` if check failed
        """
        for rec in records:
            assert(rec is not None)
            if not rec.timestamp.between(timespan):
                raise TimestampError('Following record\'s timestamp is %s, which runs off %s: \n%s' %
                                     (rec.timestamp, timespan, rec))
