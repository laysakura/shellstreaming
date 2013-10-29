# -*- coding: utf-8 -*-
"""
    shellstreaming.batch_set
    ~~~~~~~~~~~~~~~~~~~~~~~~
"""


class BatchSet(object):
    def __init__(self):
        self._batches = []  # TODO: is list fast/useful enough?

    def add(self, batch):
        # assert: no 2 batches are in charge of the same timestamp
        assert(self.find_batch(batch.get_timestamp_start())   is None)
        assert(self.find_batch(batch.get_timestamp_end() - 1) is None)

        # TODO: inserting batch into better index (for performance)
        self._batches.append(batch)

    def find_batch(self, timestamp):
        for batch in self._batches:
            if batch.get_timestamp_start() <= timestamp < batch.get_timestamp_end():
                return batch
        return None

    def pop(self):
        # TODO: return batch with oldest timestamp?
        try:
            return self._batches.pop()
        except IndexError as e:
            return None

    def __len__(self):
        return len(self._batches)
