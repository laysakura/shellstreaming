# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.filter_split
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides filtering operators with multiple outputs
"""
from relshell.recorddef import RecordDef
from shellstreaming.core.batch import Batch
from shellstreaming.operator.base import Base


class FilterSplit(Base):
    """"""

    def __init__(self, *conditions, **kw):
        """

        :param conditions: tuple of conditions.
            Each condition is simply `eval`ed after replacing column name into actual value.
        """
        self._conditions = conditions
        in_qs, out_qs = (kw['input_queues'], kw['output_queues'])

        # input queue
        assert(len(in_qs) == 1)
        self._in_q = in_qs.values()[0]
        # output queues
        # self._out_qs = {<condition>: <BatchQueue instance>, ...}
        assert(len(out_qs) >= 1)
        self._out_qs = {}
        for cond in conditions:
            for edge_id, q in out_qs.iteritems():
                if edge_id.endswith(cond):
                    self._out_qs[cond] = q

        Base.__init__(self)

    def run(self):
        """Filter batch according to :param:`*conditions`
        """
        while True:
            batch = self._in_q.pop()
            if batch is None:
                map(lambda q: q.push(None), self._out_qs.values())
                break

            # filter records by conditions

            # make `eval`able conditions
            rdef = batch.record_def()
            eval_conditions = [FilterSplit._colnames_to_colrefs(cond, rdef, 'rec') for cond in self._conditions]
            # record list to pack into Batch
            out_batch_recs = {cond: [] for cond in self._conditions}

            # append each record to appropreate `out_batch_recs`
            for rec in batch:
                for i in xrange(len(self._conditions)):
                    orig_cond, eval_cond = (self._conditions[i], eval_conditions[i])
                    if eval(eval_cond):
                        out_batch_recs[orig_cond].append(rec)
                        break  # next record

            # push filtered records as Batches
            for cond in self._conditions:
                out_batch = Batch(rdef, tuple(out_batch_recs[cond]))
                self._out_qs[cond].push(out_batch)

    @staticmethod
    def out_stream_edge_id_suffixes(conditions):
        return conditions

    @staticmethod
    def _colnames_to_colrefs(s, rdef, record_var_name):
        """

        >>> rdef = RecordDef([{'name': 'col0'}, {'name': 'col1'}, {'name': 'col2'}])
        >>> FilterSplit._colnames_to_colrefs('col2', rdef, 'rec')
        'rec[2]'
        >>> FilterSplit._colnames_to_colrefs('col0 == 100 and col1!=col2', rdef, 'rec')
        'rec[0] == 100 and rec[1]!=rec[2]'
        """
        for i in xrange(len(rdef)):
            col = rdef[i].name
            s = s.replace(col, '%s[%d]' % (record_var_name, i))
        return s
