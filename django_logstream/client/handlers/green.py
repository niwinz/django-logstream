# -*- coding: utf-8 -*-
# Copyright (c) 2011 Andrei Antoukh <niwi@niwi.be>

from gevent_zeromq import zmq
from gevent.queue import Queue
from gevent import spawn
from logging import StreamHandler

from logserverd.common import Singleton
from logserverd.client.handlers.common import InfiniteRotatingFileHandler as CommonIRFH


class InfiniteRotatingFileHandler(CommonIRFH):
    __metaclass__ = Singleton
    _queue = Queue()
    def __init__(self, *args, **kwargs):
        super(InfiniteRotatingFileHandler, self).__init__(*args, **kwargs)
        spawn(self._loop)

    def _loop(self):
        while True:
            record = self._queue.get()
            super(InfiniteRotatingFileHandler, self).emit(record)

    def emit(self, record):
        self._queue.put_nowait(record)


class CollectorHandler(StreamHandler):
    __metaclass__ = Singleton
    _queue = Queue()

    def __init__(self, address = 'ipc:///tmp/collector.sock', *args, **kwargs):
        super(CollectorHandler, self).__init__(*args, **kwargs)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.connect(address)
        spawn(self._loop)

    def _loop(self):
        while True:
            self.socket.send_json(self._queue.get())

    def emit(self, record):
        self._queue.put_nowait({'type':'stream', 'text': self.format(record)})
