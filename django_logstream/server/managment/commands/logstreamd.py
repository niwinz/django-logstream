# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError

import pyzmq


class Command(BaseCommand):
    def handle(self, *args, **options):
        pass
