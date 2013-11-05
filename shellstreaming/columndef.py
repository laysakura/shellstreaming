# -*- coding: utf-8 -*-
"""
    shellstreaming.columndef
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides column definitions.
"""
import re
from shellstreaming.error import UnsupportedTypeError, ColumnDefError
from shellstreaming.type import Type


class ColumnDef(object):
    """Specifies column's features (name, type, ...)."""

    required_fields = [
        'name',
    ]
    """Required fields for column definition.

    :param name: name of column with `name_format <#shellstreaming.columndef.ColumnDef.name_format>`_
    """

    optional_fields = [
        'type',
    ]
    """Optional fields for column definition.

    :param type: shellstream types used for strict type checking (one of `Type.type_list <#shellstreaming.type.Type.type_list>`_)
    """

    name_format = '^[_a-zA-Z][_a-zA-Z0-9]*$'
    """`name` field's format. """
    _pat_name = re.compile(name_format)

    # APIs
    def __init__(self, column_def):
        """Creates column definition object.

        :param column_def: e.g. ``{'name': 'col1', 'type': 'STRING'}``
        :raises:           `ColumnDefError <#shellstreaming.error.ColumnDefError>`_
        """
        ColumnDef._chk_unsupported_fields(column_def)
        ColumnDef._chk_required_fields(column_def)
        self._set_attrs(column_def)

    # Private functions
    @staticmethod
    def _chk_unsupported_fields(coldef):
        all_fields = set(ColumnDef.required_fields) | set(ColumnDef.optional_fields)
        for k in coldef.iterkeys():
            if k not in all_fields:
                raise ColumnDefError("Key '%s' is invalid" % (k))

    @staticmethod
    def _chk_required_fields(coldef):
        for k in ColumnDef.required_fields:
            if k not in coldef.keys():
                raise ColumnDefError("Key '%s' is required" % (k))

    def _set_attrs(self, coldef):
        # required attributes
        self.name = ColumnDef._gen_name(coldef['name'])
        # optional attributes
        if 'type' in coldef: self.type = ColumnDef._gen_type(coldef['type'])

    @staticmethod
    def _gen_name(name):
        if not ColumnDef._pat_name.match(name):
            raise ColumnDefError("'%s' is invalid for 'name'" % (name))
        return name

    @staticmethod
    def _gen_type(_type):
        try:
            return Type(_type)
        except UnsupportedTypeError as e:
            raise ColumnDefError("%s")
