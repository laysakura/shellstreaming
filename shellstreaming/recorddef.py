'''recorddef.py
'''
# -*- coding: utf-8 -*-
from shellstreaming.error import BaseError


class RecordDef(object):
    """Record definition."""
    # APIs
    def __init__(self, type_def):
        """Constructor.

        @param type_def  an array defining record type.
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
        """
        self._typedef = type_def

    def __len__(self):
        return len(self._typedef)

    def __getitem__(self, key):
        return self._typedef[key]


class RecordTypeError(BaseError):
    """An exception raised when a record does not match with RecordDef."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class RecordDefError(BaseError):
    """An exception raised when input to RecordDef is invalid data structure."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
