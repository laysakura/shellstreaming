# -*- coding: utf-8 -*-
"""
    shellstreaming.batch
    ~~~~~~~~~~~~~~~~~~~~

    :synopsis: Set of records assembled by timestamp.

    From users' perspective, `Batch` is equivalent to so-called `window` in stream processing's context.
    Also, a `Batch` is passed to an operator at-a-time internally.
"""
import os
from shellstreaming.error import TimestampError


class Batch(object):
    """Set of records assembled by timestamp"""
    def __init__(self, timespan, records, timestamp_check=False):
        """Create an *immutable* batch of records

        :param timespan: timespan of this batch
        :param records:  records
        :type record:    instance of `tuple`
        :param timestamp_check: if `True`, checks timestamp of each record is between `[timestamps_start, timestamps_end)`
        :raises: TimestampError when at least one of record's timestamp exceeds `[timestamps_start, timestamps_end)`
        """
        assert(isinstance(records, tuple))

        self.timespan = timespan
        self._records      = records
        self._records_iter = iter(records)

        if timestamp_check:
            Batch._chk_timestamp(self.timespan, self._records)

    def __str__(self):
        ret_str_list = ['(%s' % (os.linesep)]
        for i in xrange(len(self._records)):
            ret_str_list.append('    %s%s' % (self._records[i], os.linesep))
        ret_str_list.append(')%s' % (os.linesep))
        return ''.join(ret_str_list)

    def __iter__(self):
        return self

    def next(self):
        """Return one of record in this batch in out-of-order.

        :raises: `StopIteration` when no more record is in this batch
        """
        # [todo] - return record with oldest timestamp? => possible if using Queue.PriorityQueue
        return next(self._records)

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
