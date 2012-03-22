# -*- coding: utf-8 -*-

from django.conf import settings
from django_logstream.utils import Singleton

from Queue import Queue
from thread import start_new_thread
from threading import Lock
from logging import StreamHandler
import zmq, copy

from Crypto.Cipher import Blowfish
from Crypto.Hash import SHA

class ZeroMQHandler(StreamHandler):
    __metaclass__ = Singleton
    _queue = Queue()

    def __init__(self, alias, address = 'ipc:///tmp/logstream_receiver', 
                                    auth={}, encrypt=False, *args, **kwargs):

        super(ZeroMQHandler, self).__init__(*args, **kwargs)
        self.alias = alias
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.connect(address)
        self.cipher_enabled = encrypt
        self.auth = auth
        start_new_thread(self._loop, ())

    def _encrypt_str(self, data):
        res = len(data) % 8
        if res != 0:
            data = data + "\0" * (8-res)
        return self.cipher.encrypt(data)

    def _encrypt(self, obj):
        newobj = copy.deepcopy(obj)
        newobj['alias'] = self._encrypt_str(obj['alias'].encode('utf-8'))
        newobj['record'] = self._encrypt_str(obj['record'].encode('utf-8'))
        return newobj

    def _loop(self):
        self.cipher = Blowfish.new(settings.SECRET_KEY)
        while True:
            data = self._queue.get(True)
            if self.cipher_enabled:
                data = self._encrypt(data)
            self.socket.send_pyobj(data)

    def _hash_message(self, obj):
        nobj = copy.deepcopy(obj)
        for key, value in obj.iteritems():
            if not isinstance(value, (str, unicode)):
                continue

            if isinstance(value, unicode):
                value = value.encode('utf-8')

            nobj[key + "_sha"] = SHA.new(value).hexdigest()
        return nobj

    def emit(self, record):
        send_obj = self._hash_message({
            'alias': self.alias,
            'record': self.format(record),
            'encrypt': self.cipher_enabled,
        })
        self._queue.put_nowait(send_obj)
