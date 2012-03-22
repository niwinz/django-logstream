# -*- coding: utf-8 -*-
# Copyright (c) 2011 Andrei Antoukh <niwi@niwi.be>

import re, os, codecs, time, logging, io
from stat import ST_DEV, ST_INO, ST_MTIME

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_unicode

log = logging.getLogger('logserverd')

class Storage(object):
    interval_unit = 60
    #interval_unit = 30
    enabled = True
    alias_list = {}
    callback = lambda x,y: x

    def _get_logpath(self):
        return getattr(settings, 'LOGSTREAM_STORAGE_PATH')

    def _get_interval(self):
        return self.interval_unit
    
    def __init__(self, interval=60, encoding=None, mode='a'):
        log.info("Itializing storage...")
        self.encoding = encoding
        self.mode = mode
        self.interval = self._get_interval() * interval
        self.suffix = "%Y-%m-%d_%H-%M-%S"
        self.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$")
        self._initial_check()

    def _initial_check(self):
        logpath = self._get_logpath()
        if not os.path.exists(logpath):
            os.mkdir(logpath)

    def _computeRollover(self, currentTime):
        result = currentTime + self.interval
        return result

    def _inter_check(self, alias):
        if alias not in self.alias_list:
            logpath = self._get_logpath()
            self.alias_list[alias] = {
                'path': os.path.join(logpath, alias),
            }
        
            if not os.path.exists(self.alias_list[alias]['path']):
                os.mkdir(self.alias_list[alias]['path'])
    
            current_log_file = os.path.join(
                self.alias_list[alias]['path'], 'current.log')

            self.alias_list[alias]['filepath'] = current_log_file
            self.alias_list[alias]['stream'] = self._open(alias)

            if not os.path.exists(current_log_file):
                self.alias_list[alias]['rolloverAt'] = self._computeRollover(int(time.time()))
            else:
                self.alias_list[alias]['rolloverAt'] = self._computeRollover(os.stat(current_log_file)[ST_MTIME])

        elif self._shouldRollover(alias):
            self._doRollover(alias)

    def setRolloverCallback(self, function):
        """Set callback function. This called on rollover opetation
        are finished. The first argument is the filepath of new file.

        :param function function: Callback function instance.
        :returns: None
        """
        self.callback = function

    def _shouldRollover(self, alias):
        """
        Determine if rollover should occur
        
        :param str alias: alias name
        :return: True or False
        :rtype: bool
        """

        t = int(time.time())
        if t >= self.alias_list[alias]['rolloverAt']:
            return True
        return False

    def _open(self, alias):
        filepath = self.alias_list[alias]['filepath']
        return io.open(filepath, 'a', encoding='utf-8')

    def _doRollover(self, alias):
        """
        Rollover logfile for alias.

        :param str alias: alias name
        :return: Nothink
        :rtype: None
        """

        filepath = self.alias_list[alias]['filepath']
        if "stream" in self.alias_list[alias]:
            self.alias_list[alias]['stream'].close()
            del self.alias_list[alias]['stream']

        t = self.alias_list[alias]['rolloverAt'] - self.interval
        timeTuple = time.gmtime(t)

        dfn = alias + "." + time.strftime(self.suffix, timeTuple)
        if os.path.exists(dfn):
            os.remove(dfn)
        
        new_filepath = os.path.join(self.alias_list[alias]['path'], dfn)
        os.rename(filepath, new_filepath)
        self.callback(new_filepath)

        self.alias_list[alias]['stream'] = self._open(alias)

        currentTime = int(time.time())
        newRolloverAt = self._computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval

        self.alias_list[alias]['rolloverAt'] = newRolloverAt
            
    def insert(self, alias, record):
        """Save logrecord on logfile."""

        self._inter_check(alias)
        if self.enabled:
            self.alias_list[alias]['stream'].write(force_unicode(record + '\n'))
            self.alias_list[alias]['stream'].flush()
