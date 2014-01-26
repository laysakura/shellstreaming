# -*- coding: utf-8 -*-
"""
    shellstreaming.core.batch_queue
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides queue of output batch

    Simple wrapper of internal queue class
"""
import Queue as q


class BatchQueue(object):
    """Queue of output batch"""

    # [todo] - use ActiveMQ for performance?

    def __init__(self):
        """Constructor"""
        self._q       = q.Queue()
        self._records = 0

    def push(self, batch):
        """"""
        self._q.put(batch)
        if batch is not None:
            self._records += len(batch)
            import logging
            logger = logging.getLogger('TerminalLogger')
            logger.warn('push: records: %d' % (self._records))

    def pop(self):
        """"""
        batch = self._q.get(timeout=365 * 24 * 60 * 60)  # workaround: enable Ctrl-C http://bugs.python.org/issue1360
        if batch is None:
            self.push(None)  # supply `None` again in case other consumers are informed `empty`
            return None
        self._records -= len(batch)
        import logging
        logger = logging.getLogger('TerminalLogger')
        logger.warn('pop: records: %d' % (self._records))
        return batch

    def records(self):
        return self._records
