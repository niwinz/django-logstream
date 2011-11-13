.. django-logstream documentation master file, created by
   sphinx-quickstart on Sun Nov 13 19:41:46 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

django-logstream
================

Introduction
------------

The python and django logging really works very well, but we run into problems when 
we have more than one instance (process) that has to write the logs into one file.

``django-logstream`` solves this problem by maintaining a separate process that receives 
logs from all other processes and properly managed logs.

Currently ``django-logstream`` uses ZeroMQ to communicate with the server request logs.

Features currently implemented:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* alias for receive multiple streams.
* logrotate by time interval.


Features implemented in future:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Encription and authentication for untrusted networks.
* size logrotate option.


How-To setup logstream daemon
-----------------------------

As a first step, we add ``LOGSTREAM_STORAGE_PATH`` to the ``settings.py``. This will tell 
the server where they host all the logs.

Add ``django_logstream.server`` to ``INSTALLED_APPS`` list.

And as the last step, we start the service with: ``python2 manage.py logstreamd``.


How-To setup logstream client/s
-------------------------------

As the first and only step, configure your logging in django settings.py.

This is an posible example:

.. code-block:: python

    LOGGING = {
        [...]
        'handlers': {
            'logstream': {
                'level': 'DEBUG',
                'class': 'django_logstream.client.handlers.threaded.ZeroMQHandler',
                'alias': 'myfirsttest',
                'address': 'ipc:///tmp/logstream_receiver', # this is a default
            }
        },
        'loggers': {
            [...]
            'yourlogger': {
                'level': 'DEBUG',
                'handler': ['logstream'],
                'propagate': False,
            }
        }
    }


.. .. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

