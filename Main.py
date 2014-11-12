from HiveLib import HiveConf, HiveLoop, HiveLog
from Handlers import HandleImporter

__author__ = 'William C. Donaldson'

LOGTAG = 'MAIN'


if __name__ == '__main__':

    HiveLog.log(LOGTAG, 'Beginning Handler Import')
    HandleImporter.handler_import(HiveConf.RPCDIR)
    HiveLog.log(LOGTAG, 'Finished Handler Import')

    HiveLog.log(LOGTAG, 'Beginning Main Loop')
    HiveLoop.MAIN_LOOP.run_forever()
    HiveLog.log(LOGTAG, 'Main Loop Ended - Hive Will Exit')