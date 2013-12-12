# -*- coding: utf-8 -*-
"""
    shellstreaming.comm.inputstream_dispatcher
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Dispatcher of inputstreams for master
"""
import rpyc
from shellstreaming.config import Config


class InputStreamDispatcher(object):
    """Asynchronous inputstream dispatcher"""
    def __init__(self, worker, inputstream_name, inputstream_args):
        """Create inputstream dispatcher

        :param worker:           worker's reachable hostname or IP address
        :param inputstream_name: class name of inputstreams
        :param inputstream_args: arguments for specified inputstream
        """
        self._conn = InputStreamDispatcher._connect(worker)
        self._async_res = InputStreamDispatcher._async_execute(self._conn, inputstream_name, inputstream_args)

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

    @staticmethod
    def _connect(worker):
        """Connect to worker"""
        connection  = rpyc.connect(worker, int(Config.instance().get('worker', 'port')))
        conn_thread = rpyc.BgServingThread(connection)
        return (worker, connection, conn_thread)

    @staticmethod
    def _async_execute(conn, inputstream_name, inputstream_args):
        """Asynchronously execute inputstream on worker process"""
        (worker, connection, conn_thread) = conn
        executor = connection.root.InputStreamExecutor(
            conn,
            inputstream_name, inputstream_args,
            on_new_batch=InputStreamDispatcher._reg_new_batch
        )

        # asynchronously call `InputStreamExecutor.exposed_execute`, in which callbacks are called
        aexecute = rpyc.async(executor.execute)
        return aexecute()

    @staticmethod
    def _reg_new_batch(conn, batch_id):
        """Register newly created batch (called by master)"""
        (worker, connection, conn_thread) = conn
        print('[%s] new batch: %s' % (worker, batch_id))
        # [todo] - implement
