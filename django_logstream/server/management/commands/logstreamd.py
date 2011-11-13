# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError

from django_logstream.server import get_backend

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            bk = get_backend()
            bk.wait()
        except KeyboardInterrupt:
            print "Exiting..."
            bk.terminate()
