import asyncio

import Common
from messagewriter import NetworkMessage


class AsyncTCPClient():
    def __init__(self, heartbeat_interval, MESSAGE_HANDLERS, loop):
        # Client control
        self.MESSAGE_HANDLERS = MESSAGE_HANDLERS
        self.CLIENT_CONTROL = {'Connected': False, 'Authenticated': False, 'Heartbeat': heartbeat_interval}
        self.loop = loop
        # Client Data
        self.servers = {}

    @asyncio.coroutine
    def client(self, *async_coroutines):
        # This can be used for something...
        for coroutine in async_coroutines:
            asyncio.async(coroutine(self.CLIENT_CONTROL))

    @asyncio.coroutine
    def connect(self, server):
        if not self.CLIENT_CONTROL['Connected']:
            print('Connecting to server {}'.format(server))
            if server in self.servers:
                print('Opening connection')
                server_info = self.servers[server]
                # Open connection to server
                self.reader, self.writer = yield from asyncio.open_connection(server_info[0],
                                                                              server_info[1],
                                                                              loop=self.loop)
                # Begin message handling and heartbeat
                asyncio.async(self.handle_message())
                asyncio.async(self.heartbeat())

                # Set Connected state
                self.CLIENT_CONTROL['Connected'] = True

    @asyncio.coroutine
    def add_server(self, name, address, port):
        self.servers[name] = [address, port]

    @asyncio.coroutine
    def heartbeat(self):
        while self.CLIENT_CONTROL['Connected']:
            yield from asyncio.sleep(self.CLIENT_CONTROL['Heartbeat'])
            msg = NetworkMessage(Common.ClientMessageType.HEARTBEAT)
            yield from msg.send(self.writer)

    @asyncio.coroutine
    def handle_message(self):
        while self.CLIENT_CONTROL['Connected']:
            msg = NetworkMessage()
            # TODO: REPLACE EXCEPTION HANDLING WHEN DONE WITH FUNNY BUSINESS
            #try:
            yield from msg.receive(self.reader)
            #print('Got message of type: {}'.format(msg.msg_type))
            if str(msg.msg_type) in self.MESSAGE_HANDLERS:
                yield from self.MESSAGE_HANDLERS[str(msg.msg_type)](msg.message_stream, self.writer)
            #except Exception as inst:
            #    print('Error while reading message! Closing connection.')
            #    self.CLIENT_CONTROL['Connected'] = False
            #    self.writer.close()

    def server_message_handler(self, func):
        @asyncio.coroutine
        def meta_func(message_stream, write_stream):
            print('Handled server message type {}'.format(func.__name__))
            yield from func(message_stream, write_stream)
        self.MESSAGE_HANDLERS['ServerMessageType.' + func.__name__] = meta_func