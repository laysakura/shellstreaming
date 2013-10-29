# -*- coding: utf-8 -*-
"""
    shellstreaming.batch_set
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Set of batches.
"""


class BatchSet(object):
    """Set of batches.

    Purpose of this class is to provide fast way to select a batch who has specific record
    (Provides timestamp index in other words).
    """
    def __init__(self):
        """Constructor"""
        self._batches = []  # TODO: is list fast/useful enough?

    def add(self, batch):
        """Add `batch` to this batch set.

        .. note::
            `[batch.get_timestamp_start(), batch.get_timestamp_end())` must not overwrap with other batches' ones.
        """
        # assert: no 2 batches are in charge of the same timestamp
        assert(self.find_batch(batch.get_timestamp_start())   is None)
        assert(self.find_batch(batch.get_timestamp_end() - 1) is None)

        # TODO: inserting batch into better index (for performance)
        self._batches.append(batch)

    def find_batch(self, timestamp):
        """Find a batch who is in charge of `timestamp`.

        :returns: None when no batch is in charge of `timestamp`
        """
        for batch in self._batches:
            if batch.get_timestamp_start() <= timestamp < batch.get_timestamp_end():
                return batch
        return None

    def pop(self):
        """Pop (fetch & remove) a batch from this batch set in out-of-order.

        :returns: None when no batch is in this batch set.
        """
        # TODO: return batch with oldest timestamp?
        try:
            return self._batches.pop()
        except IndexError as e:
            return None

    def __len__(self):
        """Return number of batches in this batch set.
        """
        return len(self._batches)
