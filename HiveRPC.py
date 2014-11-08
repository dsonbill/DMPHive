__author__ = 'William C. Donaldson'

import HiveLog

RPC_REGISTER = {}
LOGTAG = 'HIVERPC'


def RPCHandler(func):
    def metafunc(*args, **kwargs):
        HiveLog.debug(LOGTAG, "Called RPC Handler  [ {} ]  With Args  [ {}, {} ]", func.__name__, args, kwargs)
        func(*args, **kwargs)
    RPC_REGISTER[func.__name__] = metafunc
    HiveLog.debug(LOGTAG, 'Registered RPC Handler  [ {} ]', func.__name__)