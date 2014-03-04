# -*- coding: utf-8 -*-
"""
    shellstreaming.istream.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides abstract istream
"""
# my module
from shellstreaming.core.batch import Batch
from shellstreaming.core.base_job import BaseJob


class Base(BaseJob):
    """Base class for istream
    """

    def __init__(self, output_queue, records_in_batch, max_records=None):
        """Constructor

        :param output_queue:  queue to output batches
        :param records_in_batch: to assemble records as batch
        :param max_input_records: istream finishes after outputting this number of records
        """
        self._batch_q       = output_queue
        self._rec_in_batch  = records_in_batch
        self._max_records   = max_records
        self._num_records   = 0

        # for creating batches one by one
        self._next_batch_span = None
        self._next_batch      = None

        BaseJob.__init__(self)

    def interrupt(self):
        """API to safely kill data-fetching thread.
        """
        self._batch_q.push(None)  # producer has end data-fetching
        BaseJob.interrupt(self)

    def add(self, rdef, record):
        """Function for istream subclasses to add records fetched.

        .. warning::
            Current constraint: `record.timestamp` of formmer must be not greater than that of later one.
            i.e. asserting ``rec1.timestamp <= rec2.timestamp`` where ``add(rec1) ; add(rec2)``

            Therefore, current version does not support user-defined timestamp.

        :param rdef:   Give valid `class`:RecordDef: even when record is `None`.
        :param record: Give `None` to signal consumer that data-fetching process has end.
        """
        # [todo] - record.timestamp is asserted as arrival time. User defined timestamp is not supported.
        # [todo] - Infosphere supports this feature by `punctuation`
        # [todo] - http://pic.dhe.ibm.com/infocenter/streams/v2r0/index.jsp?topic=%2Fcom.ibm.swg.im.infosphere.streams.spl-language-specification.doc%2Fdoc%2Fpunctuation.html

        def _when_got_last_record():
            if self._next_batch:
                _produce_next_batch()
            self._batch_q.push(None)  # tell downstreams no more batch will arrive
            self.interrupt()

        def _produce_next_batch():
            batch = Batch(rdef, tuple(self._next_batch))
            self._batch_q.push(batch)

        def _create_next_batch():
            self._next_batch = []

        # finish istream when getting None
        if record is None:
            _when_got_last_record()
            return

        if self._next_batch is None:
            _create_next_batch()

        self._next_batch.append(record)

        if len(self._next_batch) == self._rec_in_batch:
            # this record is for 2nd batch
            _produce_next_batch()
            _create_next_batch()

        # Finish istream after outputing enough records or data source has no more data.
        self._num_records += 1
        if self._max_records and self._num_records == self._max_records:
            _when_got_last_record()
            return
