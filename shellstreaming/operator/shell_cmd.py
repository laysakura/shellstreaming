# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.shell_cmd
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides shell command operators
"""
# standard modules
import re

# my modules
from relshell.recorddef import RecordDef
from relshell.shelloperator import ShellOperator
from shellstreaming.operator.base import Base


class ShellCmd(Base):
    """"""

    def __init__(self, cmd, **kw):
        """
        1入力専門

        :param conditions: tuple of conditions.
            Each condition is simply `eval`ed after replacing column name into actual value.
        """
        self._cmd = ShellCmd.cmd_to_relshellcmd(cmd)
        self._kw  = kw
        in_qs, out_qs = (kw['input_queues'], kw['output_queues'])

        # input queue
        assert(len(in_qs) == 1)
        self._in_q = in_qs.values()[0]
        # output queues
        assert(len(out_qs) == 1)
        self._out_q = out_qs.values()[0]

        Base.__init__(self)

    def run(self):
        """
        """
        while True:
            batch = self._in_q.pop()
            if batch is None:
                self._out_q.push(None)
                break

            op = ShellOperator(
                self._cmd,
                # pass keyword args to relshell
                **{k: self._kw[k] for k in self._kw if k in ShellCmd.relshell_ShellOperator_args()}
            )
            out_batch = op.run(in_batches=(batch, ))

            self._out_q.push(out_batch)

    @staticmethod
    def out_stream_edge_id_suffixes(args):
        cmd = args[0]
        return (cmd[:min(20, len(cmd))] + '...', )

    @staticmethod
    def cmd_to_relshellcmd(cmd):
        return cmd.replace('IN_STREAM', 'IN_BATCH0').replace('OUT_STREAM', 'OUT_BATCH')

    @staticmethod
    def relshell_ShellOperator_args():
        return [
            'out_record_def',
            'out_col_patterns',
            'success_exitcodes',
            'in_record_sep',
            'in_column_sep',
        ]
