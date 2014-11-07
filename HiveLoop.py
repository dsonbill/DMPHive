__author__ = 'William C. Donaldson'

import asyncio
import asyncio_redis
import HiveLog

MAIN_LOOP = asyncio.get_event_loop()
SERVICE_CHANNELS = []
SERVICE_CHANNEL_REGISTER = {}


@asyncio.coroutine
def hive_subscriber():
    """
    Subscribes to the functions tagged with @ChannelHandler, and send messages to them as appropriate.
    Runs asynchronously.
    """
    connection = yield from asyncio_redis.Connection.create(host='localhost', port=6379)

    # Create subscriber.
    subscriber = yield from connection.start_subscribe()
    # Subscribe to channel.
    yield from subscriber.subscribe(SERVICE_CHANNELS)
    # Wait for incoming events.

    while True:
        reply = yield from subscriber.next_published()
        HiveLog.log('REDIS', 'Received  [ {} ]  on channel  [ {} ]'.format(reply.value, reply.channel), 'LOG')
        try:
            SERVICE_CHANNEL_REGISTER[reply.channel](reply.value)
        except Exception as inst:
            HiveLog.log('REDIS', 'Exception  [ {} ]  occurred while trying to handle message  [ {} ]  on channel  [ {} ]'.format(type(inst), reply.value, reply.channel), 'ERROR')


def ChannelHandler(func):
    def metafunc(*args, **kwargs):
        HiveLog.log('REDIS', "Called function  [ {} ]  with args  [ {}, {} ]".format(func.__name__, args, kwargs), 'DEBUG')
        func(*args, **kwargs)
    SERVICE_CHANNEL_REGISTER[func.__name__] = metafunc
    SERVICE_CHANNELS.append(func.__name__)
    HiveLog.log('REDIS', 'Registered channel handler  [ {} ]'.format(func.__name__), 'DEBUG')


asyncio.async(hive_subscriber(), loop=MAIN_LOOP)