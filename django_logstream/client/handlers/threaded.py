# -*- coding: utf-8 -*-

from django_logstream.utils import Singleton

from Queue import Queue
from thread import start_new_thread
from threading import Lock
from logging import StreamHandler
import zmq


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
