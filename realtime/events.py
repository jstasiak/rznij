# -*- coding: utf-8 -*-
class EventDispatcher(object):
    event_handler_chains = {}

    @classmethod
    def handler_chain_for_event(class_object, event_name):
        chains = class_object.event_handler_chains
        if event_name not in chains:
            chains[event_name] = []

        return chains[event_name]

    @classmethod
    def bind(class_object, event_name, handler):
        chain = class_object.handler_chain_for_event(event_name)
        chain.append(handler)

    @classmethod
    def unbind(class_object, event_name, handler):
        chain = class_object.handler_chain_for_event(event_name)
        chain.remove(handler)

    @classmethod
    def fire(class_object, event):
        chain = class_object.handler_chain_for_event(event.name)
        for handler in chain:
            handler(event)


class Event(object):
    def __init__(self, connection, data):
        self.acknowledged = False
        self.connection = connection
        self.name = data['name']
        self.args = data.get('args')
        self.event_id = data.get('id')

    @property
    def acknowledgeable(self):
        return bool(self.event_id)

    def ack(self, params):
        assert self.acknowledgeable
        assert not self.acknowledged

        socket = self.connection.socket
        socket.ack(self.event_id, [params])




