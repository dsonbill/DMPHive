from HiveLib import HiveLog
import asyncio
from re import split
from aiozmq import rpc

__author__ = 'William C. Donaldson'

event_loop = asyncio.get_event_loop()
address = '127.0.0.1'
port = '5555'
pyhackery = []

RPCREGISTER = {}

@asyncio.coroutine
def client_loop():

    client = yield from rpc.connect_rpc(connect='tcp://{}:{}'.format(address, port))

    pyhackery.append(client)
    while True:
        proc_command(input('{}# '.format(address)))


def proc_command(string_input):
    if ' ' in string_input:
        try:
            comlist = split(' ', string_input)
            func = comlist.pop(0)
            try:
                RPCREGISTER[func](*comlist)
            except KeyError:
                HiveLog.log('COMPROC', 'Command \'{}\' does not exist!'.format(func))
            except Exception as inst:
                print('COMPROC', 'Exception  [ {} ]  While Handling Command  [ {} ]  List  [ {} ]'.format(type(inst), func, comlist))
        except Exception as inst:
            print('COMPROC', 'Exception  [ {} ]  In Command Handler'.format(type(inst)))
    else:
        try:
            RPCREGISTER[string_input]()
        except KeyError:
            HiveLog.log('COMPROC', 'Command \'{}\' does not exist!'.format(string_input))
        except Exception as inst:
            print('COMPROC', 'Exception  [ {} ]  While Handling Command  [ {} ]'.format(type(inst), string_input))


def RPCCOM(func):
    def metafunc(*args, **kwargs):
        HiveLog.debug('COMRPC', "Sent Remote Command  [ {} ]  With Args  [ {}, {} ]", func.__name__, args, kwargs)
        return func(pyhackery[0].call, *args, **kwargs)
    RPCREGISTER[func.__name__] = metafunc
    HiveLog.log('COMRPC', 'Registered Remote Command  [ {} ]'.format(func.__name__))


@RPCCOM
def shutdown(call):
    call.shutdown()


event_loop.run_until_complete(client_loop())