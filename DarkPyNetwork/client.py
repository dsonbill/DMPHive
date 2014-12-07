import os
import asyncio
import configparser

import xmlrsa
from DarkPyNetwork import log, conf
from DarkPyNetwork.message_parsing import NetworkMessage
from DarkPyNetwork.message_handling import MessageHandlerRegister


class AsyncTCPClient():
    def __init__(self, loop, data_dir, configuration, message_handlers, name='PyClient', log_tag='CLIENT',
                 receive_handler_name='ServerMessageType',
                 send_handler_name='ClientMessageType'):
        # Client control
        self.loop = loop
        self.connected = asyncio.Event(loop=self.loop)
        self.disconnecting = asyncio.Event(loop=self.loop)
        self.authenticated = asyncio.Event(loop=self.loop)

        # Client config
        self.name = name
        self.log_tag = log_tag
        self.data_dir = data_dir
        self.configuration = configuration.client.config

        # Client Handler
        self.protocol = message_handlers.protocol
        self.h_receive = message_handlers.Client.receive
        self.h_send = message_handlers.Client.send
        self.receive_handler = getattr(self.h_receive, receive_handler_name)
        self.send_handler = getattr(self.h_send, send_handler_name)
        self.receive_handler_type = getattr(self.protocol, receive_handler_name)
        self.send_handler_type = getattr(self.protocol, send_handler_name)

        # Client RSA encryption object
        # Check if data_dir is a valid directory
        if os.path.isdir(data_dir):
            private_key_file = os.path.join(data_dir, self.configuration['KEY']['private'])
            if os.path.isfile(private_key_file):
                self.crsa = xmlrsa.RSA()
                self.crsa.load_keys_xml(private_key_file)
            else:
                self.crsa = xmlrsa.RSA(1024)
                self.crsa.save_keys_xml(private_key_file)
        else:
            # data_dir is not a valid directory! Throw an attribute exception!
            raise AttributeError('AsyncTCPClient needs a valid directory for data_dir!')

    @asyncio.coroutine
    def connect(self, server):
        if not self.connected.is_set():

            log.log(self.log_tag, 'Connecting To Server {}:{}', server[0], server[1])

            # Set IP/Domain and port
            self.domain = server[0]
            self.port = server[1]

            # Open connection to server
            self.reader, self.writer = yield from asyncio.open_connection(server[0],
                                                                          server[1],
                                                                          loop=self.loop)

            # Log State
            self.log_tag = '{} - {}:{}'.format(self.name, server[0], server[1])
            log.log(self.log_tag, 'Connected To Server {}:{}', server[0], server[1])

            # Begin message handling and heartbeat
            asyncio.async(self.receive(), loop=self.loop)
            asyncio.async(self.heartbeat(), loop=self.loop)

            # Set Connected state
            self.connected.set()

    @asyncio.coroutine
    def disconnect(self, reason='Connection Closing', *formatargs):
        if self.connected.is_set() and not self.disconnecting.is_set():
            reason_text = 'Client Closing Connection  [ {} ]'.format(reason)
            log.log(self.log_tag, reason_text, *formatargs)
            self.disconnecting.set()
            yield from self.send_handler.CONNECTION_END(self, reason)

    @asyncio.coroutine
    def close_connection(self):
        if self.connected.is_set() and self.disconnecting.is_set():
            # Set connected state to false
            self.connected.clear()
            self.disconnecting.clear()

            # Wait 1 second before closing
            yield from asyncio.sleep(1)
            self.writer.close()

    @asyncio.coroutine
    def heartbeat(self):
        yield from self.connected.wait()
        while self.connected.is_set():
            #print(connected)
            log.debug(self.log_tag, 'Sending Message Of Type  [ ClientMessageType HEARTBEAT ]')
            yield from self.send_handler.HEARTBEAT(self)

    @asyncio.coroutine
    def send(self, client_msg_type, *args, **kwargs):
        if self.connected.is_set() and not self.disconnecting.is_set():
            msg_space, msg_type = str.split(str(client_msg_type), '.')
            log.debug(self.log_tag, 'Sending Message Of Type  [ {} {} ]',
                      msg_space, msg_type)
            if hasattr(self.send_handler, msg_type):
                #yield from self.message_handlers[str(msg.msg_type)](self, msg)
                message_handler = getattr(self.send_handler, msg_type)
                asyncio.async(message_handler(self, *args, **kwargs), loop=self.loop)
            else:
                log.debug(self.log_tag, 'Warning: No Message Handler For Type  [ {} {} ]',
                          'ClientMessageType', msg_type)

    @asyncio.coroutine
    def receive(self):
        #yield from self.connected.wait()
        while self.connected.is_set():

            # TODO: REPLACE EXCEPTION HANDLING WHEN DONE WITH FUNNY BUSINESS
            # Try to read a message. Failure means we totally lose sync; we must then abandon the connection
            try:
                # Read a message into a NetworkMessage object
                msg = NetworkMessage()
                success = yield from msg.read(self.receive_handler_type, self.reader)
                if not success:
                    # return on unsuccessful message read
                    return

                # Get message type and space
                msg_space, msg_type = str.split(str(msg.msg_type), '.')
                log.debug(self.log_tag, 'Received Message Of Type  [ {} {} ]',
                          msg_space, msg_type)

                # Try to handle the message we received. Failure does not desync at this point,
                # so we can just log the exception and try to keep going.
                try:

                    # Check if a handler function exists in the receive handler
                    if hasattr(self.receive_handler, msg_type):
                        # Get message handler for received message type and pass it client and message
                        message_handler = getattr(self.receive_handler, msg_type)
                        yield from message_handler(self, msg)

                    # We don't have a handler for that message type, log if we are debugging.
                    else:
                        log.debug(self.log_tag, 'Warning: No message handler for type  [ {} {} ]',
                                  msg_space, msg_type)

                # We've had an exception handling the message; log the except and try to keep going.
                except Exception as inst:
                    log.exception(self.log_tag, 'Trying To Handle Server Message', inst)
            # We've had an exception reading from the stream; this means total failure, so log the exception
            # and disconnect the client.
            except Exception as inst:
                log.exception(self.log_tag, 'Trying To Read Server Message', inst)
                self.disconnect()


class ClientManager():
    def __init__(self, root_dir,
                 data_dir='Data',
                 default_client_config=None,
                 message_handlers=None,
                 loop=None,
                 log_tag='ClientManager'):

        # Check if there is no loop
        if loop is None:
            self.loop = asyncio.new_event_loop()
        else:
            self.loop = loop

        # Directories
        self.root_dir = root_dir
        self.data_dir = os.path.join(root_dir, data_dir)
        # Check if the Data directory exists
        if not os.path.isdir(self.data_dir) and os.path.isdir(root_dir):
            # Directory does not exist, make sure there is no filename conflict
            if not os.path.exists(self.data_dir):
                # Should be safe to make a directory, just try it.
                os.makedirs(self.data_dir)
            else:
                raise FileExistsError('Data dir exists, but it is not a directory!')

        # Check if there is no default config
        if default_client_config is None:
            # Build default client configuration
            default_conf = configparser.ConfigParser()
            default_conf['KEY'] = {}
            default_conf['KEY']['private'] = 'privkey.xml'

            self.default_client_config = default_conf
        else:
            self.default_client_config = default_client_config

        # Client configuration storage
        self.conf_man = conf.DarkConfigManager(self.data_dir)

        # Message Handler Register
        if message_handlers is None:
            try:
                self.message_handlers = MessageHandlerRegister(self.conf_man.main.config['HANDLERS']['folder'])
            except:
                print('Could not automagically import client message handlers.')
                raise AttributeError('ClientManager message_handlers MUST be defined properly.')

        # Clients - single and "multi-server"
        self.clients = {}
        self.multiclients = {}

        # Logging
        self.log_tag = log_tag
        log.Debugging = bool(self.conf_man.main.config['LOGGING']['debugging'])
        log.Loop = self.loop

    def add_client(self, name='PyClient', multiconnect=False, client_count=0, log_tag='CLIENT'):
        # Client data dir
        client_data = os.path.join(self.data_dir, name)

        # Check if the client's directory exists
        if not os.path.isdir(client_data) and not os.path.exists(client_data):

            # Should be safe, just try it
            try:
                os.makedirs(client_data)

            # Log and return on failure
            except Exception as inst:
                log.exception(self.log_tag, 'Creating Client Directory  [ {} ]',
                              inst, client_data)
                return

        # Add client configuration
        self.conf_man.add_config(name)
        self.conf_man.add_config_file(name, 'client', self.default_client_config)

        # Add client if it does not exist and is not a multiconnect client
        if name not in self.clients and name not in self.multiclients and not multiconnect:
            # Add Client
            self.clients[name] = AsyncTCPClient(self.loop,
                                                client_data,
                                                self.conf_man.get_config(name),
                                                self.message_handlers,
                                                name,
                                                log_tag)

        # Make sure we are allowed to multiconnect and there are no other client by name
        elif name not in self.clients and multiconnect:

            # Check if we need to initialize the multiconnect client
            if name not in self.multiclients:
                self.multiclients[name] = []

            # Add Clients
            for client_no in range(client_count):
                self.multiclients[name].append(AsyncTCPClient(self.loop,
                                                              client_data,
                                                              self.conf_man.get_config(name),
                                                              self.message_handlers,
                                                              name,
                                                              log_tag))

    def connect_client(self, server, port, name='PyClient'):
        # Make sure we have the client specified
        if name in self.clients:

            # Make sure the client is not already connected to something
            if self.clients[name].connected.is_set():

                # Log error and return
                log.error(self.log_tag,
                          'Unable To Connect: Client  [ {} ]  Already Connected To  [ {}:{} ]',
                          name, self.clients[name].server, self.clients[name].port)
                return

            # Log connection attempt and schedule connect command
            log.log(self.log_tag, 'Client  [ {} ]  Connecting To Server  [ {}:{} ]', name, server, port)
            asyncio.async(self.clients[name].connect([server, port]), loop=self.loop)

        # Make sure we have the client specified
        elif name in self.multiclients:
            # Get the number of clients we have in the multiclient dict
            clients = len(self.multiclients[name])

            # Check if we have enough clients to fulfil the connect request
            if clients == len(server):
                log.error(self.log_tag, 'Multiclient  [ {} ]  Error: Not Enough Clients For Server Count', name)
            # Iterate over range instead of list so we know where we are
            for client_number in range(len(self.multiclients[name])):

                # Make sure the client is not already connected to something
                if self.multiclients[name][client_number].connected.is_set():

                    # Log error and return
                    log.error(self.log_tag,
                              'Unable To Connect: Client  [ {} ]  Already Connected To  [ {}:{} ]',
                              name, self.clients[name].server, self.clients[name].port)
                    return

                # Log connection attempt and schedule connect command
                log.log(self.log_tag, 'Client  [ {} ]  Connecting To Server  [ {}:{} ]',
                        name, server[client_number], port[client_number])
                asyncio.async(self.multiclients[name][client_number].connect([server[client_number],
                                                                              port[client_number]]),
                              loop=self.loop)

        # Unable to connect client to server
        else:
            log.error(self.log_tag, 'Unable To Connect: Client  [ {} ]  Not Found Or Bad Argument', name)

    def disconnect_all(self, reason='ClientManager Closing Clients'):
        # Handle single-connect clients
        for client in self.clients:
            # Try to disconnect the client
            try:
                asyncio.async(self.clients[client].disconnect(reason), loop=self.loop)
            # Log exception during disconnect
            except Exception as inst:
                log.exception(self.log_tag, 'Closing Client Connection', inst)

        # Handle multiconnect clients
        for client_name in self.multiclients:
            for client in self.multiclients[client_name]:
                # Try to disconnect the client
                try:
                    asyncio.async(client.disconnect(reason),
                                  loop=self.loop)
                # Log exception during disconnect
                except Exception as inst:
                    log.exception(self.log_tag, 'Closing Client Connection', inst)