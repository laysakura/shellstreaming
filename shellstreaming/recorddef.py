'''recorddef.py
'''
# -*- coding: utf-8 -*-
from error import ColumnDefError, RecordDefError
from columndef import ColumnDef


class RecordDef(object):
    """Record definition."""
    # APIs
    def __init__(self, record_def):
        """Constructor.

        @example
            rdef = RecordDef(
                [
                    {'name'        : 'col1',
                     'type'        : 'STRING',
                     'primary_key' : True,
                    },
                    {'name'        : 'col2',
                     'type'        : 'INT',
                    },
                ]
            )
            rdef[1].name  # => 'col2'
            rdef[1].type  # => Type('INT')

        For each column specification, following keys are supported.
        (See: ColumnDef.required_keys, ColumnDef.optional_keys)

        @param record_def  an array defining record type.
            e.g.

        @raises RecordDefError
        """
        self._recdef = record_def
        self._set_coldefs()

    def __len__(self):
        return len(self._coldefs)

    def __getitem__(self, key):
        return self._coldefs[key]

    # Private functions
    def _set_coldefs(self):
        self._coldefs = []
        for i, raw_coldef in enumerate(self._recdef):
            try:
                self._coldefs.append(ColumnDef(raw_coldef))
            except ColumnDefError as e:
                raise RecordDefError("In column %d: %s" % (i, e))
