'''record.py
'''
# -*- coding: utf-8 -*-
from error import RecordTypeError, UnsupportedTypeError
from type import Type


class Record(object):
    """Record"""
    # APIs
    def __init__(self, record_def, *args):
        """Checks if type of `rec` matches `recdef`
        @param record_def  instance of RecordDef
        @param *args       columns
        @raises  RecordTypeError
        """
        self._rec    = Record._internal_repl(args)
        self._recdef = record_def
        Record._chk_type(self._recdef, self._rec)

    def __str__(self):  # pragma: no cover
        retstr = "("
        for i in xrange(len(self._rec)):
            retstr += "%s: %s, " % (self._recdef[i]['name'], self._rec[i])
        return retstr + ")"

    def __len__(self):
        return len(self._rec)

    # Private functions
    @staticmethod
    def _internal_repl(args):
        return tuple(args)

    @staticmethod
    def _chk_type(recdef, rec):
        """Checks if type of `rec` matches `recdef`
        @param recdef  instance of RecordDef
        @param rec     instance of Record
        @raises  RecordTypeError
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
