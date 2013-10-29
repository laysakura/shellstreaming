# -*- coding: utf-8 -*-
"""
    shellstreaming.batch
    ~~~~~~~~~~~~~~~~~~~~
"""


class Batch(object):
    def __init__(self, timestamp_start, timestamp_end):
        self._ts_start = timestamp_start
        self._ts_end   = timestamp_end
        self._records = []  # TODO: is list fast/useful enough?

    def add(self, record):
        # assert: record's timestamp is in-between batch's time range
        assert(record.timestamp >= self.get_timestamp_start())
        assert(record.timestamp <  self.get_timestamp_end())

        # TODO: inserting record into better index (for performance)
        self._records.append(record)

    def get_timestamp_start(self):
        return self._ts_start

    def get_timestamp_end(self):
        return self._ts_end

    def __len__(self):
        return len(self._records)

    def __iter__(self):
        # TODO: yield record with oldest timestamp?
        while True:
            try:
                yield self._records.pop()
            except IndexError as e:
                break
