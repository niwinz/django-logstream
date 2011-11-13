# -*- coding: utf-8 -*-
# Copyright (c) 2011 Andrei Antoukh <niwi@niwi.be>

from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
import re, glob

class InfiniteTimedRotatingFileHandler(TimedRotatingFileHandler):
    """ Infinite time rotating logging handler. """
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
        super(InfiniteTimedRotatingFileHandler, self).__init__(filename, when, interval, backupCount, encoding, delay, utc)
        self.backupCount = self.current_max_files()  

    def current_max_files(self):
        files = sorted(glob.glob("%s*" % (self.baseFilename)), reverse=True)
        return files and len(files) + 10 or 10

    def doRollover(self):
        super(InfiniteTimedRotatingFileHandler, self).doRollover()
        self.backupCount += 1


class InfiniteRotatingFileHandler(RotatingFileHandler):
    """ Infinite rotating logging handler. """
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        super(InfiniteRotatingFileHandler, self).__init__(filename, 'a', maxBytes, backupCount, encoding, delay)
        self.rx = re.compile("^[\w\d\-\/\.\_]+\.(\d+)$", flags=re.U)
        self.backupCount = int(self.current_max_files()) + 1

    def current_max_files(self):
        files = sorted(glob.glob("%s*" % (self.baseFilename)), reverse=True)
        try:
            return files and max([int(self.rx.search(x).group(1)) for x in files if self.rx.match(x)]) or 1
        except ValueError:
            return 1

    def doRollover(self):
        super(InfiniteRotatingFileHandler, self).doRollover()
        self.backupCount += 1
