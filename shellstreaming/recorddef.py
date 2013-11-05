# -*- coding: utf-8 -*-
"""
    shellstreaming.recorddef
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides DDL (like CREATE TABLE) information.
"""
from shellstreaming.error import ColumnDefError, RecordDefError
from shellstreaming.columndef import ColumnDef


class RecordDef(object):
    """Used as DDL (like CREATE TABLE) information."""
    # APIs
    def __init__(self, record_def):
        """Creates an object with each column property from `record_def`.

        :param record_def: list of column definition hash (see example below)

        *Example:*

        ::

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

        .. seealso::

            `ColumnDef.required_fields <#shellstreaming.columndef.ColumnDef.required_fields>`_ and
            `ColumnDef.optional_fields <#shellstreaming.columndef.ColumnDef.optional_fields>`_
            for each column's specification.
        """
        self._recdef = record_def
        self._set_coldefs()

    def __len__(self):
        """Returns number of columns"""
        return len(self._coldefs)

    def __getitem__(self, key):
        """Returns specified column definition.

        :param key: column index to get definition.
        :type key:  int (0-origin)
        :rtype:     `ColumnDef <#shellstreaming.columndef.ColumnDef>`_
        """
        return self._coldefs[key]

    # Private functions
    def _set_coldefs(self):
        self._coldefs = []
        for i, raw_coldef in enumerate(self._recdef):
            try:
                self._coldefs.append(ColumnDef(raw_coldef))
            except ColumnDefError as e:
                raise RecordDefError("In column %d: %s" % (i, e))
