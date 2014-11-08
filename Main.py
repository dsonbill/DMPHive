from HiveLib import HiveConf, HiveLoop, HiveLog
import os

__author__ = 'William C. Donaldson'

LOGTAG = 'MAIN'


if __name__ == '__main__':
    # Import RPC Handlers
    for (root, dirs, files) in os.walk(HiveConf.RPCDIR):
        for file in files:
            try:
                module_name = os.path.splitext(file)[0]
                __import__('Handlers.RPCHandlers.{}'.format(module_name),
                           globals(),
                           locals(),
                           fromlist=['Handlers.RPCHandlers'])
                HiveLog.log(LOGTAG, 'Imported RPC Handler  [ {} ]', module_name)
            except Exception as inst:
                HiveLog.error(LOGTAG, 'Exception  [ {} ]  Importing RPC Handler  [ {} ]', type(inst), file)
        break

    # Import Redis Subscription Handlers
    for (root, dirs, files) in os.walk(HiveConf.SUBDIR):
        for file in files:
            try:
                module_name = os.path.splitext(file)[0]
                __import__('Handlers.SubHandlers.{}'.format(module_name),
                           globals(),
                           locals(),
                           fromlist=['Handlers.SubHandlers'])
                HiveLog.log(LOGTAG, 'Imported Subscription Handler  [ {} ]', module_name)
            except Exception as inst:
                HiveLog.error(LOGTAG, 'Exception  [ {} ]  Importing Subscription Handler  [ {} ]', type(inst), file)
        break

    HiveLoop.MAIN_LOOP.run_forever()