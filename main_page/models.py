# -*- coding: utf-8 -*-

import re

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.db import models
from django.utils.translation import ugettext as _

from realtime.util import success, failure
from realtime.events import EventDispatcher

class Shortcut(models.Model):
    shortcut = models.TextField(unique = True, db_index = True)
    url = models.TextField(db_index = True, validators = [URLValidator])
    created_at = models.DateTimeField(auto_now_add = True, db_index = True)
    use_count = models.IntegerField(default = 0, db_index = True)

    def bump_use_count(self):
        self.use_count += 1
        self.save()

    @classmethod
    def normalize_shortcut(class_object, shortcut):
        return re.sub(r'[\s/?&%]]', '-', shortcut)

    def clean(self):
        self.shortcut = Shortcut.normalize_shortcut(self.shortcut)

        if not self.shortcut:
            while not self.shortcut or not Shortcut.is_available(self.shortcut):
                self.shortcut = User.objects.make_random_password()

    @classmethod
    def is_available(class_object, shortcut):
        shortcut = class_object.normalize_shortcut(shortcut)
        return len(class_object.objects.filter(shortcut = shortcut)) == 0


def handle_shortcut_availability(event):
    shortcut = Shortcut.normalize_shortcut(event.args[0])
    available = Shortcut.is_available(shortcut)
    event.ack(success(available = available))

EventDispatcher.bind('shortcut_availability', handle_shortcut_availability)


def handle_create_shortcut(event):
    data = event.args[0]

    shortcut = data.get('shortcut', '')
    if shortcut and not Shortcut.is_available(shortcut):
        event.ack(failure(message = _('Skrót {0!r} jest juz zajety').format(shortcut)))
        return

    url = data.get('url')
    if not url.startswith('http'):
        url = 'http://' + url

    try:
        URLValidator()(url)
    except:
        event.ack(failure(message = _('Adres {0!r} jest niepoprawnym URL-em').format(url)))
        return

    shortcut = Shortcut(shortcut = shortcut, url = url)
    shortcut.full_clean()
    shortcut.save()
    event.ack(success(shortcut_url = 'http://{0}/{1}'.format(settings.SERVER_ADDRESS, shortcut.shortcut)))

EventDispatcher.bind('create_shortcut', handle_create_shortcut)

