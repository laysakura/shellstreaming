class BaseError(Exception):
    """Base class for exceptions in this module."""
    pass


class UnsupportedTypeError(BaseError):
    """An exception raised when unsupported type is used"""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ColumnDefError(BaseError):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


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
