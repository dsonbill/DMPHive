__author__ = 'William C. Donaldson'

import HiveLoop
import HiveLog
import os

WDIR = os.path.dirname(os.path.abspath(__file__))
RPCDIR = os.path.join(WDIR, 'Handlers', 'RPCHandlers')
SUBDIR = os.path.join(WDIR, 'Handlers', 'SubHandlers')


if __name__ == '__main__':
    # Import RPC Handlers
    for (dirpath, dirnames, filenames) in os.walk(RPCDIR):
        for file in filenames:
            try:
                module_name = os.path.splitext(file)[0]
                __import__('Handlers.RPCHandlers.{}'.format(module_name), globals(), locals(), fromlist=['Handlers.RPCHandlers'])
                HiveLog.log('MAIN', 'Imported RPC Handler  [ {} ]'.format(module_name))
            except Exception as inst:
                HiveLog.log('MAIN', 'Exception  [ {} ]  occurred while importing RPC Handler  [ {} ]'.format(type(inst), file), 'ERROR')
        break

    # Import Redis Subscription Handlers
    for (dirpath, dirnames, filenames) in os.walk(SUBDIR):
        for file in filenames:
            try:
                module_name = os.path.splitext(file)[0]
                __import__('Handlers.SubHandlers.{}'.format(module_name), globals(), locals(), fromlist=['Handlers.SubHandlers'])
                HiveLog.log('MAIN', 'Imported Subscription Handler  [ {} ]'.format(module_name))
            except Exception as inst:
                HiveLog.log('MAIN', 'Exception  [ {} ]  occurred while importing Subscription Handler  [ {} ]'.format(type(inst), file), 'ERROR')
        break

    HiveLoop.MAIN_LOOP.run_forever()