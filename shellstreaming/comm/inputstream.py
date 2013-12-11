# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.inputstream
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Dispatch | Execute inputstreams
"""
import rpyc
from importlib import import_module
from shellstreaming.config import Config


class InputStreamExecutorService(rpyc.Service):  # pragma: no cover
                                                 # Because this class is executed by separated process,
                                                 # it's difficult to trace execution of statements inside it.
                                                 # [todo] - must be tested
    """Provides `InputStreamExecutor <shellstreaming.comm.InputStreamExecutorService.exposed_InputStreamExecutor>`_ for worker.

    .. note::
        Any class & functions in `InputStreamExecutorService` are executed by worker process.
    """
    class exposed_InputStreamExecutor(object):
        """Asynchronous executor of inputstreams"""
        def __init__(self, conn, inputstream_name, inputstream_args, on_new_batch):
            """Creates asynchronous executor of inputstreams

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

            This function is supposed to be wrapped by `rpyc.async`
            """
            stream = InputStreamExecutorService._create_stream(self._inputstream_name, self._inputstream_args)
            for batch in stream:
                InputStreamExecutorService._store_new_batch(batch)
                self._on_new_batch(self._conn, batch)

    @staticmethod
    def _create_stream(inputstream_name, inputstream_args):
        """Create stream object"""
        module       = import_module(InputStreamExecutorService._get_module_name(inputstream_name))
        stream_class = getattr(module, inputstream_name)
        stream       = stream_class(*inputstream_args)
        return stream

    @staticmethod
    def _get_module_name(inputstream_name):
        """Return full module path of `inputstream_name`"""
        module = 'shellstreaming.inputstream.%s' % (inputstream_name.lower())
        return module

    @staticmethod
    def _store_new_batch(batch):
        """Store batch into worker's memory"""
        pass
        # print('[worker] new batch is stored: %s' % (batch))
        # [todo] - put batch into worker's memory


class InputStreamDispatcher(object):
    """Asynchronous inputstream dispatcher"""
    def __init__(self, worker, inputstream_name, inputstream_args):
        """Create inputstream dispatcher

        :param worker:           worker's reachable hostname or IP address
        :param inputstream_name: class name of inputstreams
        :param inputstream_args: arguments for specified inputstream
        """
        self._conn = _connect(worker)
        self._async_res = _async_execute(self._conn, inputstream_name, inputstream_args)

    def join(self):
        """Wait for inputstream to finish.

        After inputstream finishes, connection to worker is closed.

        :raises: any exception raised from `_async_execute`
        """
        self._async_res.wait()
        if self._async_res.error:  # pragma: no cover
            raise self._async_res.value

        (worker, connection, conn_thread) = self._conn
        conn_thread.stop()
        connection.close()


def _connect(worker):
    """Connect to worker"""
    connection  = rpyc.connect(worker, int(Config.instance().get('worker', 'port')))
    conn_thread = rpyc.BgServingThread(connection)
    return (worker, connection, conn_thread)


def _async_execute(conn, inputstream_name, inputstream_args):
    """Asynchronously execute inputstream on worker process"""
    (worker, connection, conn_thread) = conn
    executor = connection.root.InputStreamExecutor(
        conn,
        inputstream_name, inputstream_args,
        on_new_batch=_reg_new_batch
    )

    # asynchronously call `InputStreamExecutor.exposed_execute`, in which callbacks are called
    aexecute = rpyc.async(executor.execute)
    return aexecute()


def _reg_new_batch(conn, batch_id):
    """Register newly created batch (called by master)"""
    (worker, connection, conn_thread) = conn
    print('[%s] new batch: %s' % (worker, batch_id))
    # [todo] - implement
