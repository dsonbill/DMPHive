from HiveLib import HiveLog
import os

__author__ = 'William C. Donaldson'

LOGTAG = 'IMPORT'


def handler_import(folder, tag):
    # Import Handlers
    for (root, dirs, files) in os.walk(folder):
        handle_folder = os.path.basename(os.path.normpath(os.path.dirname(os.path.abspath(__file__))))
        folder_name = '{}.{}'.format(handle_folder, os.path.basename(os.path.normpath(root)))
        if 'Standard.py' in files:
            files.insert(0, files.pop(files.index('Standard.py')))
        else:
            HiveLog.debug(LOGTAG, 'Standard {} Library Not Found! Skipping List Reorder.', tag)
        for file in files:
            try:
                module_name = os.path.splitext(file)[0]
                __import__('{}.{}'.format(folder_name, module_name),
                           globals(),
                           locals(),
                           fromlist=[folder_name])
                HiveLog.log(LOGTAG, 'Imported {} Handler  [ {} ]', tag, module_name)
            except Exception as inst:
                HiveLog.error(LOGTAG, 'Exception  [ {} ]  Importing {} Handler  [ {} ]', type(inst), tag, file)
        break