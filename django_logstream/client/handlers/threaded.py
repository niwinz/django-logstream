# -*- coding: utf-8 -*-

from django_logstream.utils import Singleton
from django_logstream.client.handlers.common import \
    InfiniteRotatingFileHandler as CommonIRFH

from Queue import Queue
from thread import start_new_thread
from threading import Lock
from logging import StreamHandler
import zmq


class InfiniteRotatingFileHandler(CommonIRFH):
    _queue = Queue()
    def __init__(self, *args, **kwargs):
        super(InfiniteRotatingFileHandler, self).__init__(*args, **kwargs)
        start_new_thread(self._loop)

    def _loop(self):
        while True:
            record = self._queue.get(True)
            super(InfiniteRotatingFileHandler, self).emit(record)

    def emit(self, record):
        self._queue.put_nowait(record)


class ZeroMQHandler(StreamHandler):
    __metaclass__ = Singleton
    _queue = Queue()

    def __init__(self, alias, address = 'ipc:///tmp/logstream_receiver', *args, **kwargs):
        super(ZeroMQHandler, self).__init__(*args, **kwargs)
        self.alias = alias
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.connect(address)
        start_new_thread(self._loop, ())

    def _loop(self):
        while True:
            self.socket.send_pyobj(self._queue.get(True))

    def emit(self, record):
        self._queue.put_nowait({'alias':self.alias, 'record': self.format(record)})
