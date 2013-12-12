# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.inputstream_executor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Executor of inputstreams for workers
"""
from importlib import import_module


class InputStreamExecutor(object):
    """Executor of inputstreams for worker processes"""
    def __init__(self, conn, inputstream_name, inputstream_args, on_new_batch):
        """Creates executor of inputstreams

        :param conn:             connection info
        :type conn:              `(worker name, result of rpyc.connection(), connection thread)`
        :param inputstream_name: class name of inputstreams
        :param inputstream_args: arguments for specified inputstream
        :type inputstream_args:  `tuple`
        :param on_new_batch:     callback function called when new batch is created
        """
        self._conn             = conn
        self._inputstream_name = inputstream_name
        self._inputstream_args = inputstream_args
        self._on_new_batch     = on_new_batch

    def exposed_execute(self):
        """Start inputsream.

        This function is supposed to be called by master process.
        """
        stream = InputStreamExecutor._create_stream(self._inputstream_name, self._inputstream_args)
        for batch in stream:
            InputStreamExecutor._store_new_batch(batch)
            self._on_new_batch(self._conn, batch)

    @staticmethod
    def _create_stream(inputstream_name, inputstream_args):
        """Create stream object"""
        module       = import_module(InputStreamExecutor._get_module_name(inputstream_name))
        stream_class = getattr(module, inputstream_name)
        stream       = stream_class(*inputstream_args)
        return stream

    @staticmethod
    def _store_new_batch(batch):
        """Store batch into worker's memory"""
        pass
        # print('[worker] new batch is stored: %s' % (batch))
        # [todo] - put batch into worker's memory

    @staticmethod
    def _get_module_name(inputstream_name):
        """Return full module path of `inputstream_name`"""
        module = 'shellstreaming.inputstream.%s' % (inputstream_name.lower())
        return module
