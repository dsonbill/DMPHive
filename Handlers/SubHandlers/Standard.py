__author__ = 'William C. Donaldson'

import HiveLog
import HiveLoop
import HiveRPC
import json


@HiveLoop.ChannelHandler
def HIVERPC(json_msg):
    try:
        rpcjson = json.loads(json_msg)
        rpcargs = json.loads(rpcjson['args'])

        HiveLog.log('HIVERPC', 'Received RPC request  [ {} ]  with args  [ {} ]'.format(rpcjson['cmd'], rpcjson['args']), 'DEBUG')

        if rpcjson['cmd'] in HiveRPC.RPC_REGISTER:
            try:
                HiveRPC.RPC_REGISTER[rpcjson['cmd']](**rpcargs)
            except Exception as inst:
                HiveLog.log('HIVERPC', 'Exception  [ {} ]  occurred while calling function  [ {} ] with JSON  [ {} ]'.format(type(inst), rpcjson['cmd'], json_msg), 'ERROR')
        else:
            HiveLog.log('HIVERPC', 'Could not handle request  [ {} ]  with args  [ {} ]'.format(rpcjson['cmd'], rpcargs), 'ERROR')

    except Exception as inst:
        HiveLog.log('HIVERPC', 'Exception  [ {} ]  occurred while decoding JSON  [ {} ]'.format(type(inst), json_msg), 'ERROR')