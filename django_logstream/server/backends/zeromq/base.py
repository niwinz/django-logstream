# -*- coding: utf-8 -*-

from django.conf import settings
from django_logstream.utils import Singleton
from django_logstream.server import storage

from multiprocessing import Process

import zmq
import Queue
import copy

from Crypto.Cipher import Blowfish
from Crypto.Hash import SHA


class WorkerProcessor(object):
    def __init__(self):
        print "Initializing WorkerProcessor class..."

    def __call__(self, queue):
        print "Running WorkerProcessor thread..."

        self.logrotate_interval = int(getattr(settings,
            'LOGSTREAM_LOGROTATE_INTERVAL', 60))
        self.secure_mode = bool(getattr(settings,
            'LOGSTREAM_SECURE_MODE', False))

        self.queue = queue
        self.storage = storage.Storage(interval=self.logrotate_interval)
        self.cipher = Blowfish.new(settings.SECRET_KEY)

        while True:
            qobj = self.queue.get(block=True)
            if not self._analyze_object(qobj):
                continue
            
            is_encrypted = bool(qobj.pop('encrypt', False))
            valid = False
            if is_encrypted:
                valid, qobj = self._decrypt(qobj)
                if not valid:
                    continue
            
            # skip all unencrtypted logs on secure
            # mode is activated
            if self.secure_mode and not valid: 
                continue

            self._process_object(qobj)

    def _decrypt(self, obj):
        nobj = copy.deepcopy(obj)
        valid = True

        for key, value in obj.iteritems():
            if not isinstance(value, (str, unicode)):
                continue
            if key.endswith("_sha"):
                continue
            nobj[key] = self.cipher.decrypt(value).strip("\0")
            if SHA.new(nobj[key]).hexdigest() != \
                                    nobj[key + '_sha']:
                valid = False
            del nobj[key + '_sha']
        return valid, nobj
    
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
    def __init__(self):
        print "Initializing WorkerReceiver class..."

    def _init(self):
        self.context = zmq.Context()
        self.bind_address = getattr(settings, 
            'LOGSTREAM_BIND_ADDR', 'ipc:///tmp/logstream_receiver')

        self.queue = Queue.Queue()

    def __call__(self):
        print "Running WorkerReceiver process..."

        self._init()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.bind(self.bind_address)

        # Starting record processor thread.
        from threading import Thread
        self.worker = Thread(target=WorkerProcessor(), args=[self.queue])
        self.worker.daemon = True
        self.worker.start()
    
        # Record receiver loop.
        while True:
            data = self.socket.recv_pyobj()
            self.queue.put_nowait(data)

    def __del__(self):
        self.worker.terminate()
        self.socket.close()


from django.core.exceptions import ImproperlyConfigured

class Backend(object):
    __metaclass__ = Singleton

    def __init__(self):
        self._check_settings()
        self.start_receiver()
        self.start_rpc()

    def _check_settings(self):
        try:
            getattr(settings, 'LOGSTREAM_STORAGE_PATH')
        except:
            raise ImproperlyConfigured('LOGSTREAM_STORAGE_PATH is not defined on yout settings')

    def start_receiver(self):
        self.process = Process(target=WorkerReceiver())
        self.process.daemon = True
        self.process.start()

    def start_rpc(self):
        pass

    def wait(self):
        self.process.join()

    def terminate(self):
        self.process.terminate()
