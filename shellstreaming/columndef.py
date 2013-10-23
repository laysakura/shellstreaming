'''columndef.py
'''
# -*- coding: utf-8 -*-
import re
from error import UnsupportedTypeError, ColumnDefError
from type import Type


class ColumnDef(object):
    required_keys = [
        'name',  # name of column
    ]
    optional_keys = [
        'type',  # ShellStream types. 'INT', 'STRING' are supported. Used for strict type checking.
    ]

    pat_name = re.compile('^[_a-zA-Z][_a-zA-Z0-9]*$')

    # APIs
    def __init__(self, column_def):
        """
        @param column_def
            E.g. {'name': 'col1', 'type': 'STRING'}

        @raises ColumnDefError
        """
        ColumnDef._chk_unsupported_keys(column_def)
        ColumnDef._chk_required_keys(column_def)
        self._set_attrs(column_def)

    # Private functions
    @staticmethod
    def _chk_unsupported_keys(coldef):
        all_keys = set(ColumnDef.required_keys) | set(ColumnDef.optional_keys)
        for k in coldef.iterkeys():
            if k not in all_keys:
                raise ColumnDefError("Key '%s' is invalid" % (k))

    @staticmethod
    def _chk_required_keys(coldef):
        for k in ColumnDef.required_keys:
            if k not in coldef.keys():
                raise ColumnDefError("Key '%s' is required" % (k))

    def _set_attrs(self, coldef):
        # required attributes
        self.name = ColumnDef._gen_name(coldef['name'])
        # optional attributes
        if 'type' in coldef: self.type = ColumnDef._gen_type(coldef['type'])

    @staticmethod
    def _gen_name(name):
        if not ColumnDef.pat_name.match(name):
            raise ColumnDefError("'%s' is invalid for 'name'" % (name))
        return name

    @staticmethod
    def _gen_type(_type):
        try:
            return Type(_type)
        except UnsupportedTypeError as e:
            raise ColumnDefError("%s")
