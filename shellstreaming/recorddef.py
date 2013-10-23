'''recorddef.py
'''
# -*- coding: utf-8 -*-
from shellstreaming.error import BaseError


class RecordDef(object):
    """Record definition."""
    # APIs
    def __init__(self, record_def):
        """Constructor.
        For each column specification, following keys are supported.
            [required]
            name : name of column

            [optional]
            type : ShellStream types.
                   'INT', 'STRING' are supported.
                   type specification is used for strict type checking.

        @param record_def  an array defining record type.
            e.g.
            [
                {'name'        : 'col1',
                 'type'        : 'STRING',
                 'primary_key' : True,
                },
                {'name'        : 'col2',
                 'type'        : 'INT',
                },
            ]

        @raises RecordDefError
        """
        self._recdef = record_def
        _chk_recdef(self._recdef)

    def __len__(self):
        return len(self._recdef)

    def __getitem__(self, key):
        return self._recdef[key]

    # Private functions
    @staticmethod
    def _chk_recdef(recdef):
        _chk_unsupported_keys(recdef)
        _chk_required_keys(recdef)
        _chk_name_col(recdef)
        _chk_type_col(recdef)

    @staticmethod
    def _chk_type(rec_

class RecordTypeError(BaseError):
    """An exception raised when a record does not match with RecordDef."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):  # pragma: no cover
        return self.msg


class RecordDefError(BaseError):
    """An exception raised when input to RecordDef is invalid data structure."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):  # pragma: no cover
        return self.msg
