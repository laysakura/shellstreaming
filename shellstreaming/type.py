'''type.py
'''
# -*- coding: utf-8 -*-
import types
from shellstreaming.error import UnsupportedTypeError


class Type:
    """Types of columns."""
    _typemap = {
        # builtin type   : shellstreaming type
        types.IntType    : 'INT',
        types.StringType : 'STRING',
    }

    # APIs
    def __init__(self, ss_type_str):
        """
        @param ss_type_str  string representing shellstreaming type.
        @raises  UnsupportedTypeError
        """
        if ss_type_str not in Type._typemap.values():
            raise UnsupportedTypeError("Type %s is not supported as shellstreaming type" %
                                       (ss_type_str))
        self._typestr = ss_type_str

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __str__(self):
        return self._typestr

    @staticmethod
    def equivalent_ss_type(val):
        """Returns Type instance representing shellstreaming type.
        @param val  value to check shellstreaming equivalent type.
        @raises  UnsupportedTypeError
        """
        builtin_type = type(val)
        if builtin_type not in Type._typemap:
            raise UnsupportedTypeError("builtin type %s is not convirtible to shellstreaming type" %
                                       (builtin_type))
        ss_type_str  = Type._typemap[builtin_type]
        return Type(ss_type_str)
