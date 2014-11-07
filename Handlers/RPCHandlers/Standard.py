__author__ = 'William C. Donaldson'

import HiveRPC
import HiveLoop


@HiveRPC.RPCHandler
def testfunc(**kwargs):
    print(kwargs['foo'])


@HiveRPC.RPCHandler
def shutdown(**kwargs):
    HiveLoop.MAIN_LOOP.stop()