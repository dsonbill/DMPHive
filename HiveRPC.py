__author__ = 'William C. Donaldson'

import HiveLog

RPC_REGISTER = {}


def RPCHandler(func):
    def metafunc(*args, **kwargs):
        HiveLog.log('HIVERPC', "Called function  [ {} ]  with args  [ {}, {} ]".format(func.__name__, args, kwargs), 'DEBUG')
        func(*args, **kwargs)
    RPC_REGISTER[func.__name__] = metafunc
    HiveLog.log('HIVERPC', 'Registered RPC function  [ {} ]'.format(func.__name__), 'DEBUG')