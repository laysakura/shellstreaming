# -*- coding: utf-8 -*-
"""
    shellstreaming.operator.shell_cmd
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides shell command operators
"""
# my modules
from relshell.shelloperator import ShellOperator
from relshell.daemon_shelloperator import DaemonShellOperator
from shellstreaming.operator.base import Base


class ShellCmd(Base):
    """"""

    def __init__(self, cmd, daemon=False, **kw):
        """
        1入力専門

        :param daemon: Whether to instanciate daemon process
        """
        self._cmd         = ShellCmd.cmd_to_relshellcmd(cmd)
        self._kw          = kw
        self._daemon      = daemon

        # instanciate daemon operator
        if daemon:
            self._daemon_op = DaemonShellOperator(
                self._cmd,
                # pass keyword args to relshell
                batch_done_indicator=kw['msg_to_cmd'],
                batch_done_output=kw['reply_from_cmd'],
                **{k: kw[k] for k in kw if k in ShellCmd.relshell_ShellOperator_args()})

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

            if not self._daemon:
                op = ShellOperator(
                    self._cmd,
                    # pass keyword args to relshell
                    **{k: self._kw[k] for k in self._kw if k in ShellCmd.relshell_ShellOperator_args()})
                out_batch = op.run(in_batches=(batch, ))
            else:
                out_batch = self._daemon_op.run(in_batches=(batch, ))

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
            # daemon
            'batch_done_indicator',
            'batch_done_output'
        ]
