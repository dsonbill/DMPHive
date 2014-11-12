from HiveLib import HiveLog
from Handlers import HandleImporter
import asyncio
from aiozmq import rpc

__author__ = 'William C. Donaldson'

MAIN_LOOP = asyncio.get_event_loop()
SERVICE_CHANNELS = []
SERVICE_CHANNEL_REGISTER = {}
LOGTAG = 'HIVELOOP'


@asyncio.coroutine
def hive_loop():
    """
    Runs the asynchronous hive loop.
    """
    HiveLog.log(LOGTAG, 'Main Loop Has Started')
    server = yield from rpc.serve_rpc(HandleImporter.Handler(), bind='tcp://127.0.0.1:5555')
    #connection = yield from asyncio_redis.Connection.create(host='localhost', port=6379)
#
    ## Create subscriber.
    #subscriber = yield from connection.start_subscribe()
    ## Subscribe to channel.
    #yield from subscriber.subscribe(SERVICE_CHANNELS)
    ## Wait for incoming events.
#
    #while True:
    #    reply = yield from subscriber.next_published()
    #    HiveLog.log(LOGTAG, 'Received  [ {} ]  On Channel  [ {} ]', reply.value, reply.channel)
    #    try:
    #        SERVICE_CHANNEL_REGISTER[reply.channel](connection, reply.value)
    #    except Exception as inst:
    #        HiveLog.error(LOGTAG,
    #                      'Exception  [ {} ]  Trying To Handle Message  [ {} ]  On Channel  [ {} ]',
    #                      type(inst), reply.value, reply.channel)


def ChannelHandler(func):
    def metafunc(*args, **kwargs):
        HiveLog.debug(LOGTAG, "Called ChannelHandler  [ {} ]  With Args  [ {}, {} ]", func.__name__, args, kwargs)
        func(*args, **kwargs)
    SERVICE_CHANNEL_REGISTER[func.__name__] = metafunc
    SERVICE_CHANNELS.append(func.__name__)
    HiveLog.debug(LOGTAG, 'Registered Channel Handler  [ {} ]', func.__name__)


asyncio.async(hive_loop(), loop=MAIN_LOOP)