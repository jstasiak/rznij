# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from django.conf import settings
from django.core.validators import URLValidator
from django.dispatch import receiver

from realtime.signals import socket_connected, socket_disconnected, socket_client_event, socket_client_event_by_type, socket_client_message
from realtime.util import failure, success

from .models import Shortcut


@receiver(socket_client_event_by_type['shortcut_availability'])
def handle_shortcut_availability(sender, request, event, **kwargs):
    shortcut = Shortcut.normalize_shortcut(event.args[0])
    available = Shortcut.is_available(shortcut)
    event.ack(success(available = available))

@receiver(socket_client_event_by_type['create_shortcut'])
def handle_create_shortcut(sender, request, event, **kwargs):
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


@receiver(socket_connected)
def handle_connected(sender, request, **kwargs):
    socket = sender
    print('{0} connected'.format(socket.session.session_id))

@receiver(socket_disconnected)
def handle_disconnected(sender, request, **kwargs):
    socket = sender
    print('{0} disconnected'.format(socket.session.session_id))

@receiver(socket_client_message)
def handle_message(sender, request, message, **kwargs):
    socket = sender
    print('{0} => message {1!r}'.format(socket.session.session_id, message))



