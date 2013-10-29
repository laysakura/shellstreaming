# -*- coding: utf-8 -*-
"""
    shellstreaming.record
    ~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides (typed|untyped) record structure.
"""
import datetime
from shellstreaming.error import RecordTypeError, UnsupportedTypeError
from shellstreaming.type import Type
from shellstreaming.timestamp import Timestamp


class Record(object):
    """Record."""

    # APIs
    def __init__(self, record_def, *columns, **kwargs):
        """Creates a record with `record_def` constraints.

        :param record_def: instance of `RecordDef <#shellstreaming.recorddef.RecordDef>`_
        :param \*columns:     contents of columns
        :param timestamp=: instance of `Timestamp <#shellstreaming.timestamp.Timestamp>`_
        :raises:           `RecordTypeError <#shellstreaming.error.RecordTypeError>`_
        """
        self._rec    = Record._internal_repl(columns)
        self._recdef = record_def
        Record._chk_type(self._recdef, self._rec)

        if 'timestamp' in kwargs:
            assert(isinstance(kwargs['timestamp'], Timestamp))
            self.timestamp = kwargs['timestamp']
        else:
            self.timestamp = Timestamp(datetime.datetime.now())

        self._cur_col = 0  # Used for `next()`

    def __str__(self):  # pragma: no cover
        """Returns string representation of record"""
        retstr = "("
        for i in xrange(len(self._rec)):
            retstr += "%s: %s, " % (self._recdef[i]['name'], self._rec[i])
        return retstr + ")"

    def __len__(self):
        """Returns number of columns in record"""
        return len(self._rec)

    def __getitem__(self, index):
        """Returns column data specified by `index`"""
        return self._rec[index]

    def __iter__(self):
        while self._cur_col < len(self._rec):
            yield self._rec[self._cur_col]
            self._cur_col += 1
        self._cur_col = 0

    # Private functions
    @staticmethod
    def _internal_repl(columns):
        return tuple(columns)

    @staticmethod
    def _chk_type(recdef, rec):
        """Checks if type of `rec` matches `recdef`
        :param recdef: instance of RecordDef
        :param rec:    instance of Record
        :raises:       `RecordTypeError <#shellstreaming.error.RecordTypeError>`_
        """
        if len(recdef) != len(rec):
            raise RecordTypeError("Number of columns is different from RecordDef")

        for i in xrange(len(recdef)):
            try:
                def_type = recdef[i].type
                col_type = Type.equivalent_ss_type(rec[i])
                if col_type != def_type:
                    raise RecordTypeError("Column %d has mismatched type:  Got '%s' [%s] ; Expected [%s]" %
                                          (i, rec[i], col_type, def_type))
            except AttributeError as e:
                # recdef[i].type is not defined, then any ShellStream type is allowed
                try:
                    Type.equivalent_ss_type(rec[i])
                except UnsupportedTypeError as e:
                    raise RecordTypeError("%s" % (e))
