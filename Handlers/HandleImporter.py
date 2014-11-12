from HiveLib import HiveLog
from aiozmq import rpc
import os
import inspect
import sys
import importlib


__author__ = 'William C. Donaldson'


LIBLIST = []
LOGTAG = 'IMPORT'


def handler_import(folder):
    # Import Handlers
    for (root, dirs, files) in os.walk(folder):
        handle_folder = os.path.basename(os.path.normpath(os.path.dirname(os.path.abspath(__file__))))
        folder_name = '{}.{}'.format(handle_folder, os.path.basename(os.path.normpath(root)))
        if 'Standard.py' in files:
            files.insert(0, files.pop(files.index('Standard.py')))
        else:
            HiveLog.debug(LOGTAG, 'Standard RPC Library Not Found! Skipping List Reorder.')
        for file in files:
            try:
                module_name = os.path.splitext(file)[0]
                HiveLog.log(LOGTAG, 'Importing RPC Handler Library  [ {} ]', module_name)
                temp_import_obj = importlib.import_module('{}.{}'.format(folder_name, module_name))
                #__import__('{}.{}'.format(folder_name, module_name),
                #           globals(),
                #           locals(),
                #           fromlist=[folder_name])
                #print(inspect.getmembers(sys.modules['{}.{}'.format(folder_name, module_name)]))
                for class_name, class_obj in inspect.getmembers(sys.modules['{}.{}'.format(folder_name, module_name)], predicate=inspect.isclass):
                    HiveLog.log(LOGTAG, 'Found RPC Command Package: {}'.format(class_name))
                    LIBLIST.append(getattr(temp_import_obj, class_name))
            except Exception as inst:
                HiveLog.error(LOGTAG, 'Exception  [ {} ]  Importing RPC Handler  [ {} ]', type(inst), file)
        break


class Handler(rpc.AttrHandler):

    def __init__(self):
        for cmdpkg in LIBLIST:
            for functupe in inspect.getmembers(cmdpkg, predicate=inspect.isfunction):
                func = getattr(cmdpkg, functupe[0])
                self.metahandler(func)

    def metahandler(self, func):
        def metafunc(*args, **kwargs):
            HiveLog.debug(LOGTAG, "Called RPC Handler  [ {} ]  With Args  [ {}, {} ]", func.__name__, args, kwargs)
            return func(*args, **kwargs)

        setattr(self, func.__name__, rpc.method(metafunc))
        HiveLog.debug(LOGTAG, 'Registered RPC Handler  [ {} ]', func.__name__)
