# -*- coding: utf-8 -*-
""":synopsis: Exception classes.

.. moduleauthor:: Sho Nakatani <lay.sakura@gmail.com>
"""


class BaseError(Exception):
    """Base class for exceptions in this module."""
    pass


class UnsupportedTypeError(BaseError):
    """An exception raised when unsupported type is used."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ColumnDefError(BaseError):
    """An exception raised when invalid column definition is used."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class RecordDefError(BaseError):
    """An exception raised when input to RecordDef is invalid data structure."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):  # pragma: no cover
        return self.msg


class RecordTypeError(BaseError):
    """An exception raised when a record does not match with RecordDef."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):  # pragma: no cover
        return self.msg
