__author__ = 'William C. Donaldson'

import HiveLoop
import HiveLog
import os

WDIR = os.path.dirname(os.path.abspath(__file__))
RPCDIR = os.path.join(WDIR, 'Handlers', 'RPCHandlers')
SUBDIR = os.path.join(WDIR, 'Handlers', 'SubHandlers')
LOGTAG = 'MAIN'


if __name__ == '__main__':
    # Import RPC Handlers
    for (root, dirs, files) in os.walk(RPCDIR):
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
    for (root, dirs, files) in os.walk(SUBDIR):
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