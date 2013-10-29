# -*- coding: utf-8 -*-
"""
    shellstreaming.batch
    ~~~~~~~~~~~~~~~~~~~~

    Set of records assembled by timestamp.

    From users' perspective, `Batch` is equivalent to so-called `window` in stream processing's context.
    Also, a `Batch` is passed to an operator at-a-time internally.
"""


class Batch(object):
    """Set of records assembled by timestamp"""
    def __init__(self, timestamp_start, timestamp_end):
        """Create a batch to assemble records whose timestamps are within `[timestamps_start, timestamps_end)`"""
        self._ts_start = timestamp_start
        self._ts_end   = timestamp_end
        self._records = []  # TODO: is list fast/useful enough?

    def add(self, record):
        """Add `record` to this batch.

        .. note::
            `record.timestamp_end` must be within `[timestamps_start, timestamps_end)`
        """
        # assert: record's timestamp is in-between batch's time range
        assert(record.timestamp >= self.get_timestamp_start())
        assert(record.timestamp <  self.get_timestamp_end())

        # TODO: inserting record into better index (for performance)
        self._records.append(record)

    def get_timestamp_start(self):
        """Return this batch's start-timestamp"""
        return self._ts_start

    def get_timestamp_end(self):
        """Return this batch's end-timestamp"""
        return self._ts_end

    def __len__(self):
        """Return number of records in this batch"""
        return len(self._records)

    def __iter__(self):
        return self

    def next(self):
        """Return one of record in this batch in out-of-order.

        :raises: `StopIteration` when no more record is in this batch
        """
        # TODO: return record with oldest timestamp?
        try:
            return self._records.pop()   # FIXME: Thread-unsafe. Possibly another thread
                                         # (typically inputstream's data-fetching thread)
                                         # can append records to this batch at the same time.
                                         # In such cases, newly-appended records are discarded.
        except IndexError as e:
            raise StopIteration(e)
