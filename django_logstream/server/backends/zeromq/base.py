# -*- coding: utf-8 -*-

from django.conf import settings
from django_logstream.utils import Singleton
from django_logstream.server import storage

from multiprocessing import Process

import zmq
import Queue

class WorkerProcessor(object):
    def __call__(self, queue):
        self.queue = queue
        self.storage = storage.Storage()

        while True:
            qobj = self.queue.get(block=True)
            if self._analyze_object(qobj):
                self._process_object(qobj)

    def _analyze_object(self, obj):
        if not isinstance(obj, dict):
            return False
        if 'alias' not in obj:
            return False
        if 'record' not in obj:
            return False

        return True

    def _process_object(self, obj):
        alias, record = obj.pop('alias'), obj.pop('record')
        self.storage.insert(alias, record)


class WorkerReceiver(object):
    def _init(self):
        self.context = zmq.Context()
        self.bind_address = getattr(settings, 
            'RECEIVER_BIND_ADDR', 'ipc:///tmp/receiver')

        self.queue = Queue.Queue()

    def __call__(self):
        self._init()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.bind(self.bind_address)

        # Starting record processor thread.
        from threading import Thread
        worker = Thread(target=WorkerProcessor(), args=[self.queue])
        worker.daemon = True
        worker.start()
    
        # Record receiver loop.
        while True:
            data = self.socket.recv_pyobj()
            self.queue.put_nowait(data)
    

class Backend(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.start_receiver()
        self.start_rpc()

    def start_receiver(self):
        self.process = Process(target=WorkerReceiver())
        self.process.daemon = True
        self.process.start()

    def start_rpc(self):
        pass
