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

        HiveLog.debug('HIVERPC', 'Received RPC Request  [ {} ]  With Args  [ {} ]', rpcjson['cmd'], rpcjson['args'])

        if rpcjson['cmd'] in HiveRPC.RPC_REGISTER:
            try:
                HiveRPC.RPC_REGISTER[rpcjson['cmd']](**rpcargs)
            except Exception as inst:
                HiveLog.error('HIVERPC',
                              'Exception  [ {} ]  Calling RPC Handler  [ {} ] With JSON  [ {} ]',
                              type(inst), rpcjson['cmd'], json_msg)
        else:
            HiveLog.error('HIVERPC',
                          'Could Not Handle RPC Request  [ {} ]  With Args  [ {} ]',
                          rpcjson['cmd'], rpcargs)

    except Exception as inst:
        HiveLog.error('HIVERPC', 'Exception  [ {} ]  Decoding JSON  [ {} ]', type(inst), json_msg)