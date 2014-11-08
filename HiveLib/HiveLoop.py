from HiveLib import HiveLog
import asyncio
import asyncio_redis

__author__ = 'William C. Donaldson'

MAIN_LOOP = asyncio.get_event_loop()
SERVICE_CHANNELS = []
SERVICE_CHANNEL_REGISTER = {}
LOGTAG = 'HIVELOOP'


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
        HiveLog.log(LOGTAG, 'Received  [ {} ]  On Channel  [ {} ]', reply.value, reply.channel)
        try:
            SERVICE_CHANNEL_REGISTER[reply.channel](reply.value)
        except Exception as inst:
            HiveLog.error(LOGTAG,
                          'Exception  [ {} ]  Trying To Handle Message  [ {} ]  On Channel  [ {} ]',
                          type(inst), reply.value, reply.channel)


def ChannelHandler(func):
    def metafunc(*args, **kwargs):
        HiveLog.debug(LOGTAG, "Called ChannelHandler  [ {} ]  With Args  [ {}, {} ]", func.__name__, args, kwargs)
        func(*args, **kwargs)
    SERVICE_CHANNEL_REGISTER[func.__name__] = metafunc
    SERVICE_CHANNELS.append(func.__name__)
    HiveLog.debug(LOGTAG, 'Registered Channel Handler  [ {} ]', func.__name__)


asyncio.async(hive_subscriber(), loop=MAIN_LOOP)