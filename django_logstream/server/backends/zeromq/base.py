# -*- coding: utf-8 -*-

from django.conf import settings
from django_logstream.utils import Singleton
from multiprocessing import Process
import zmq


class WorkerReceiver(object):
    def __init__(self):
        self.context = zmq.Context()
        self.bind_address = getattr(settings, 
            'RECEIVER_BIND_ADDR', 'ipc:///tmp/receiver')

    def __call__(self):
        self.socket = self.context.socket(zmq.PULL)
        self.socket.bind(self.bind_address)

        while True:
            data = self.socket.recv_pyobj()
    

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
