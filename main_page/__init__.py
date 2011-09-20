# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from django.conf import settings
from django.core.validators import URLValidator

from realtime.events import on_event
from realtime.util import failure, success


from .models import Shortcut

@on_event('shortcut_availability')
def handle_shortcut_availability(event):
    shortcut = Shortcut.normalize_shortcut(event.args[0])
    available = Shortcut.is_available(shortcut)
    event.ack(success(available = available))

@on_event('create_shortcut')
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


@on_event('connect')
def handle_connected(event):
    print('{0} connected'.format(event.connection.socket.session.session_id))

@on_event('disconnect')
def handle_disconnected(event):
    print('{0} disconnected'.format(event.connection.socket.session.session_id))

