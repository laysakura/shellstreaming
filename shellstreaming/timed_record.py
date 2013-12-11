# -*- coding: utf-8 -*-
"""
    shellstreaming.timed_record
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides (typed|untyped) record structure w/ timestamp.
"""
import datetime
from relshell.record import Record
from shellstreaming.error import RecordTypeError, UnsupportedTypeError
from shellstreaming.timestamp import Timestamp


class TimedRecord(Record):
    """(typed|untyped) record structure w/ timestamp."""

    # APIs
    def __init__(self, record_def, *columns, **kwargs):
        """Creates a record with `record_def` constraints.

        :param record_def: instance of `RecordDef <#shellstreaming.recorddef.RecordDef>`_
        :param \*columns:     contents of columns
        :param timestamp=: instance of `Timestamp <#shellstreaming.timestamp.Timestamp>`_
        :raises:           `RecordTypeError <#shellstreaming.error.RecordTypeError>`_
        """
        if 'timestamp' in kwargs:
            assert(isinstance(kwargs['timestamp'], Timestamp))
            self.timestamp = kwargs['timestamp']
            del kwargs['timestamp']
        else:
            self.timestamp = Timestamp(datetime.datetime.now())

        Record.__init__(self, record_def, *columns, **kwargs)
