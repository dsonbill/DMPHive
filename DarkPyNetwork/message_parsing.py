import asyncio
import struct


class NetworkMessage():
    def __init__(self):
        self.header_set = False
        self.message_stream = asyncio.StreamReader()

    def set_header(self, type_enum, msg_type=0, msg_len=0):
        # Set the type enumerator
        self.type_enum = type_enum

        # Set the message type
        if type(msg_type) is int:
            self.msg_type = self.type_enum(msg_type)
        else:
            self.msg_type = msg_type

        # Set the message length
        self.msg_length = msg_len

        # Set the header_set flag
        self.header_set = True

    @asyncio.coroutine
    def read(self, type_enum, stream):
        # Read the message header
        header = yield from stream.read(8)
        if len(header) > 0:
            header = struct.unpack('>ii', header)

            # Set header data
            self.set_header(type_enum, header[0], header[1])

            # Read the message payload and send to stream
            if self.msg_length > 0:
                # Read data from stream and stuff in message container
                message_data = yield from stream.read(self.msg_length)
                self.message_stream.feed_data(message_data)
            return True
        else:
            # Empty message, return a False
            return False

    @asyncio.coroutine
    def write(self, stream, data=b''):
        if self.header_set:
            # Get 2 instances of MessageWriter to build the message
            with MessageWriter() as mw:
                # Write the message type
                mw.write('int', self.msg_type.value)
                # Write the byte payload
                mw.write('bytes', data)
                # Write message to the stream
                stream.write(mw.data)


class MessageReader():
    def __init__(self, stream):
        self.stream = stream

    @asyncio.coroutine
    def read(self, type_string):
        if type_string is 'int':
            retval = yield from self.read_int()
        elif type_string is 'float':
            retval = yield from self.read_float()
        elif type_string is 'double':
            retval = yield from self.read_double()
        elif type_string is 'bytes':
            retval = yield from self.read_bytes()
        elif type_string is 'bool':
            retval = yield from self.read_bool()
        elif type_string is 'str':
            retval = yield from self.read_string()
        else:
            retval = None

        # Return read value
        return retval

    @asyncio.coroutine
    def read_int(self):
        data = yield from self.stream.read(4)
        return struct.unpack('!i', data)[0]

    @asyncio.coroutine
    def read_float(self):
        data = yield from self.stream.read(4)
        return struct.unpack('!f', data)[0]

    @asyncio.coroutine
    def read_double(self):
        data = yield from self.stream.read(8)
        return struct.unpack('!d', data)[0]

    @asyncio.coroutine
    def read_bytes(self):
        byte_length = yield from self.read_int()
        data = yield from self.stream.read(byte_length)
        return data

    @asyncio.coroutine
    def read_bool(self):
        data = yield from self.stream.read(1)
        return struct.unpack('?', data)[0]

    @asyncio.coroutine
    def read_string(self):
        byte_length = yield from self.read_int()
        data = yield from self.stream.read(byte_length)
        return data.decode('utf-8')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class MessageWriter():
    def __init__(self):
        self.data = b''

    def write(self, type_string, payload):
        if type_string is 'int':
            self.write_int(payload)
        elif type_string is 'float':
            self.write_float(payload)
        elif type_string is 'double':
            self.write_double(payload)
        elif type_string is 'bytes':
            self.write_bytes(payload)
        elif type_string is 'bool':
            self.write_bool(payload)
        elif type_string is 'str':
            self.write_string(payload)
        else:
            pass  # Do nothing for now, should probably have something here

    def write_int(self, number):
        self.data += struct.pack('!i', number)

    def write_float(self, number):
        self.data += struct.pack('!f', number)

    def write_double(self, number):
        self.data += struct.pack('!f', number)

    def write_bytes(self, byte_string):
        self.write_int(len(byte_string))
        self.data += byte_string

    def write_bool(self, bool_obj):
        self.data += struct.pack('?', bool_obj)

    def write_string(self, string):
        self.write_bytes(string.encode('utf-8'))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass