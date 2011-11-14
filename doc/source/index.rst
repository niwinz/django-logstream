.. django-logstream documentation master file, created by
   sphinx-quickstart on Sun Nov 13 19:41:46 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

django-logstream
================

Introduction
------------

Logging of python is great and the intagracion of django with python logging, it is also very good. 
But sometimes we have to run multiple instances (processes) and want to save the logs without having problems 
with files opened by multiple processes.

``django-logstream`` solves this problem. It runs as a service (separate process) that receives logs 
of different instances, thus allowing multiple processes to the log stored in one file without any problem.

Currently, ``django-logstream`` ZeroMQ used for interprocess communication and now with integrated encryption!

Features currently implemented:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* alias for receive multiple streams.
* logrotate by time interval.
* encription and hash of all messages.


Features implemented in future:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* size logrotate option.
* rabbitmq backend. (not prioritary)
* redis backend. (not prioritary)

How-To install
--------------

.. code-block:: shell

    pip install django-logstream


How-To setup logstream daemon
-----------------------------

As a first step, we add ``LOGSTREAM_STORAGE_PATH`` to the ``settings.py``. This will tell 
the server where they host all the logs.

Add ``django_logstream.server`` to ``INSTALLED_APPS`` list.

And as the last step, we start the service with: ``python2 manage.py logstreamd``.


Other configuration options:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`LOGSTREAM_BIND_ADDR`
    ZeroMQ path for bind address. Default: ``ipc:///tmp/logstream_receiver``

`LOGSTREAM_SECURE_MODE`
    Put logstream to secure mode. In this mode only accepts encrypted and
    validated with sha1 hash messages. Default: False

`LOGSTREAM_LOGROTATE_INTERVAL`
    Set a interval in minutes for logrotate of logs. Default: 60


How-To setup logstream client
-----------------------------

As the first and only step, configure your logging in django settings.py.

This is an posible example:

.. code-block:: python
    
    LOGGING = {
        'handlers': {
            'logstream': {
                'level': 'DEBUG',
                'class': 'django_logstream.client.handlers.threaded.ZeroMQHandler',
                'alias': 'myfirsttest',
                'address': 'ipc:///tmp/logstream_receiver', # this is a default
                'encrypt': True # default is False
            }
        },
        'loggers': {
            'yourlogger': {
                'level': 'DEBUG',
                'handler': ['logstream'],
                'propagate': False,
            }
        }
    }
