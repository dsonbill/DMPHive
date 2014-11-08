from HiveLib import HiveLoop, HiveRPC

__author__ = 'William C. Donaldson'


@HiveRPC.RPCHandler
def testfunc(**kwargs):
    print(kwargs['foo'])


@HiveRPC.RPCHandler
def shutdown(**kwargs):
    HiveLoop.MAIN_LOOP.stop()