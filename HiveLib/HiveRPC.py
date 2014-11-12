from HiveLib import HiveLog

__author__ = 'William C. Donaldson'

RPC_REGISTER = {}
LOGTAG = 'HIVERPC'


def RPCHandler(func):
    def metafunc(redis_connection, *args, **kwargs):
        HiveLog.debug(LOGTAG, "Called RPC Handler  [ {} ]  With Args  [ {}, {} ]", func.__name__, args, kwargs)
        func(redis_connection, *args, **kwargs)
    RPC_REGISTER[func.__name__] = metafunc
    HiveLog.debug(LOGTAG, 'Registered RPC Handler  [ {} ]', func.__name__)