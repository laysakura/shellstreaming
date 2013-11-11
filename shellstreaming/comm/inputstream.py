# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.inputstream
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Dispatch | Execute inputstreams
"""
import rpyc
from importlib import import_module
from shellstreaming.config import config


class InputStreamExecutorService(rpyc.Service):
    """"""
    class exposed_InputStreamExecutor(object):
        def __init__(self, conn, inputstream_name, inputstream_args, on_new_batch, on_stream_close):
            """
            :param conn: for closing connection on close
            """
            self._conn             = conn
            self._inputstream_name = inputstream_name
            self._inputstream_args = inputstream_args
            self._on_new_batch     = on_new_batch
            self._on_stream_close  = on_stream_close

        def exposed_execute(self):
            """"""
            stream = InputStreamExecutorService._create_stream(self._inputstream_name, self._inputstream_args)
            for batch in stream:
                InputStreamExecutorService._store_new_batch(batch)
                self._on_new_batch(self._conn, batch)
            self._on_stream_close(self._conn)

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
        """"""
        
        print('[worker] new batch is stored: %s' % (batch))


class InputStreamDispatcher(object):
    """"""
    def __init__(self, worker, inputstream_name, inputstream_args):
        """async"""
        self._conn = _connect(worker)
        self._async_res = _async_execute(self._conn, inputstream_name, inputstream_args)

    def join(self):
        """Wait for inputstream to finish.

        After inputstream finishes, connection to worker is closed.

        :raises: any exception raised from `_async_execute`
        """
        self._async_res.wait()
        if self._async_res.error:
            raise self._async_res.value

        (worker, connection, conn_thread) = self._conn
        conn_thread.stop()
        connection.close()


def _connect(worker):
    """"""
    connection  = rpyc.connect(worker, int(config.get('worker', 'port')))
    conn_thread = rpyc.BgServingThread(connection)
    return (worker, connection, conn_thread)


def _async_execute(conn, inputstream_name, inputstream_args):
    """"""
    print('async exec')
    (worker, connection, conn_thread) = conn
    executor = connection.root.InputStreamExecutor(
        conn,
        inputstream_name, inputstream_args,
        on_new_batch=_reg_new_batch,
        on_stream_close=_close_connection
    )

    # asynchronously call `InputStreamExecutor.exposed_execute`, in which callbacks are called
    aexecute = rpyc.async(executor.execute)
    return aexecute()


def _reg_new_batch(conn, batch_id):
    """called by master, callback"""
    (worker, connection, conn_thread) = conn
    print('[%s] new batch: %s' % (worker, batch_id))


def _close_connection(conn):
    """"""
    (worker, connection, conn_thread) = conn
    print('%s\'s inputstream has closed' % (worker))
