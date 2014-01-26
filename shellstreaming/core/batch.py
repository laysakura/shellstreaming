# -*- coding: utf-8 -*-
"""
    shellstreaming.core.batch
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Simple wrapper of relshell.Batch.

    Easily on/off data type checking
"""
import relshell.batch


class Batch(relshell.batch.Batch):
    """"""

    check_datatype = True
    """This value must be set before any instance is created"""

    def __init__(self, record_def, records):
        """Constructor"""
        relshell.batch.Batch.__init__(self, record_def, records, Batch.check_datatype)
