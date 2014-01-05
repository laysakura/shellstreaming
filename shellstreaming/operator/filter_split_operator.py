# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.filter_split_operator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides filtering operators with multiple outputs
"""
from shellstreaming.operator.base import Base


class FilterSplitOperator(Base):
    def __init__(self, *conditions):
        self.conditions = conditions
        pass

    def execute(self, batch):
        pass

    @staticmethod
    def stream_names(conditions):
        return conditions
