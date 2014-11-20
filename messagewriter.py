import asyncio
import contextlib
import struct
import Common


class NetworkMessage():
    def __init__(self, msg_type=0):
        self.message_stream = asyncio.StreamReader()
        if type(msg_type) is not int:
            self.msg_type = msg_type.value
        else:
            self.msg_type = msg_type
        self.msg_length = int()

    @asyncio.coroutine
    def receive(self, stream):
        # Read the message header
        header = yield from stream.read(8)
        header = struct.unpack('<ii', header)
        self.msg_type = Common.ServerMessageType(header[0])
        self.msg_length = header[1]

        # Read the message payload and send to stream
        if self.msg_length > 0:
            # Cut off the accidental double prefix length
            self.msg_length -= 4
            yield from stream.read(4)
            message_data = yield from stream.read(self.msg_length)
            self.message_stream.feed_data(message_data)

    @asyncio.coroutine
    def send(self, stream, data=b''):
        # Get 2 instances of MessageWriter to build the message
        with message_writer() as mw1:
            with message_writer() as mw2:
                # Write the payload to byte envelope mw2
                mw2.write('bytes', data)
                # Write the message type to mw1
                mw1.write('int', self.msg_type)
                # Write the mw2 byte payload to mw1
                mw1.write('bytes', mw2.data)
                # Send mw1 over the network
                stream.write(mw1.data)


class MessageReader():
    def __init__(self, stream):
        self.stream = stream

    @asyncio.coroutine
    def read(self, type_string):
        if type_string is 'int':
            data = yield from self.stream.read(4)
            return struct.unpack('<I', data)
        if type_string is 'bytes':
            byte_length = yield from self.stream.read(4)
            byte_length = struct.unpack('<I', byte_length)[0]
            data = yield from self.stream.read(byte_length)
            return data
        if type_string is 'bool':
            data = yield from self.stream.read(1)
            return struct.unpack('?', data)
        if type_string is 'str':
            byte_length = yield from self.stream.read(4)
            byte_length = struct.unpack('<I', byte_length)[0]
            data = yield from self.stream.read(byte_length)
            return data.decode('utf-16')


class MessageWriter():
    def __init__(self):
        self.data = b''

    def write(self, type_string, payload):
        if type_string is 'int':
            self.write_int(payload)
        if type_string is 'bytes':
            self.write_bytes(payload)
        if type_string is 'bool':
            self.write_bool(payload)
        if type_string is 'str':
            self.write_string(payload)

    def write_int(self, number):
        self.data += struct.pack('<I', number)

    def write_bytes(self, byte_string):
        self.write_int(len(byte_string))
        self.data += byte_string

    def write_bool(self, bool_obj):
        self.data += struct.pack('?', bool_obj)

    def write_string(self, string):
        self.write_bytes(string.encode('utf-16')[2:])


@contextlib.contextmanager
def message_reader(stream):
    try:
        yield MessageReader(stream)
    finally:
        pass


@contextlib.contextmanager
def message_writer():
    try:
        yield MessageWriter()
    finally:
        pass
