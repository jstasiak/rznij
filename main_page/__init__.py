# -*- coding: utf-8 -*-
from __future__ import print_function

from django.conf import settings
from django.core.validators import URLValidator

from .models import Shortcut
from realtime.events import EventDispatcher
from realtime.util import failure, success

def handle_shortcut_availability(event):
    shortcut = Shortcut.normalize_shortcut(event.args[0])
    available = Shortcut.is_available(shortcut)
    event.ack(success(available = available))

EventDispatcher.bind('shortcut_availability', handle_shortcut_availability)


def handle_create_shortcut(event):
    data = event.args[0]

    shortcut = data.get('shortcut', '')
    if shortcut and not Shortcut.is_available(shortcut):
        event.ack(failure(message = 'Skrót {0!r} jest juz zajety'.format(shortcut)))
        return

    url = data.get('url')
    if not url.startswith('http'):
        url = 'http://' + url

    print(url)
    try:
        URLValidator()(url)
    except:
        event.ack(failure(message = 'Adres {0!r} jest niepoprawnym URL-em'.format(url)))
        return

    shortcut = Shortcut(shortcut = shortcut, url = url)
    shortcut.full_clean()
    shortcut.save()
    event.ack(success(shortcut_url = 'http://{0}/{1}'.format(settings.SERVER_ADDRESS, shortcut.shortcut)))

EventDispatcher.bind('create_shortcut', handle_create_shortcut)


EventDispatcher.bind('connect', lambda event: print('{0} connected'.format(event.connection.socket.session.session_id)))
EventDispatcher.bind('disconnect', lambda event: print('{0} disconnected'.format(event.connection.socket.session.session_id)))

