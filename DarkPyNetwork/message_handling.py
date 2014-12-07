import os
import sys
import asyncio
import inspect
import importlib

from DarkPyNetwork import log


class Expando(object):
    pass


class MessageHandlerRegister():
    def __init__(self, handler_folder, log_tag='REGISTER', protocol_list=None, handler_list=None):
        self.root_folder = handler_folder
        self.log_tag = log_tag
        if protocol_list is None:
            self.protocol_list = ['protocol.py']
        else:
            self.protocol_list = protocol_list
        if handler_list is None:
            self.handler_list = ['receive.py', 'send.py']
        else:
            self.handler_list = handler_list

        # Get protocol from root handler folder
        self.import_handler(handler_folder, self.protocol_list, isprotocol=True)
        # Process handlers
        for folder in self.get_folders():
            self.import_handler(folder, self.handler_list)

    def new_handler_object(self, *namespaces, obj=None, instantiate=False):
        # Check if adding an actual object; otherwise, use Expando class
        # Set instantiate flag to true to actually call obj
        if obj is None:
            obj = Expando()
            instantiate = False

        # Check if we are adding a top-level object
        if len(namespaces) == 1:
            if instantiate:
                setattr(self, namespaces[0], obj())
            else:
                setattr(self, namespaces[0], obj)

        # Add non-top-level objects
        else:
            # Set the target object name
            new_name = namespaces[0]

            # Use an expando object for very easy depth perception
            current_namespace_object = Expando()

            # Process non-target namespaces
            for namespace in namespaces:
                if namespace is not new_name:
                    # Check if this is the first namespace object we are processing
                    if not hasattr(current_namespace_object, 'last'):
                        # Get the first object from the MessageHandlerRegister object
                        current_namespace_object.last = getattr(self, namespace)
                    else:
                        # Get the next object from the last object processed
                        current_namespace_object.last = getattr(current_namespace_object.last, namespace)

            # Check if we should instantiate the object or not
            if instantiate:
                # Set and instantiate target to last object processed
                setattr(current_namespace_object.last, new_name, obj())
            else:
                # Set target
                setattr(current_namespace_object.last, new_name, obj)

    def import_handler(self, folder, file_list, isprotocol=False):
        # Get relative handler path and build network handler namespace
        handler_folder = os.path.basename(os.path.normpath(os.path.dirname(os.path.abspath(folder))))
        #print(handler_folder)
        handler_name = os.path.basename(os.path.normpath(folder))
        handler_namespace = '{}.{}'.format(handler_folder, handler_name)

        # Set the parent handler object
        # This check is not necessary, but it keeps us from adding a useless Expando object
        if not isprotocol:
            self.new_handler_object(handler_name)

        # Process and import the files
        for file in file_list:

            # Make sure the files exist
            if not os.path.isfile(os.path.join(folder, file)):
                # File doesn't exist!
                log.error(self.log_tag,
                          'Fatal Import Error: {} Message Handler File {} Does Not Exist!',
                          handler_name, file)
                return
            else:
                # Process the modules
                try:
                    # Get module name
                    module_name = os.path.splitext(file)[0]

                    # protocol gets processed separately
                    if isprotocol:
                        # Get module namespace
                        module_namespace = '{}.{}'.format(handler_name, module_name)

                        # Import the module
                        importlib.import_module(module_namespace)

                        # Set module handler object
                        self.new_handler_object(module_name)

                        # Search for classes in the module
                        for name, cls in inspect.getmembers(sys.modules[module_namespace], predicate=inspect.isclass):
                            # Check if we are processing the Protocol class
                            if name == 'Protocol':
                                # Instantiate protocol.Protocol and add it to the current handler object as 'info'
                                self.new_handler_object('info', module_name,
                                                        obj=cls, instantiate=True)
                                log.debug(self.log_tag,
                                          'Imported Primary Messaging Protocol From  [ {} ]',
                                          module_namespace)

                            # Process common classes, and skip Enum since it is useless and guaranteed to show up
                            elif name != 'Enum':
                                # Add classes to the current handler object
                                self.new_handler_object(name, module_name, obj=cls)
                                log.debug(self.log_tag,
                                          'Imported  [ {} ]  Messaging Protocol Identifier  [ {} ]',
                                          module_namespace, name)

                    # Process send and receive modules
                    else:
                        # Get module namespace
                        module_namespace = '{}.{}'.format(handler_namespace, module_name)

                        # Import the module
                        importlib.import_module(module_namespace)

                        # Set module handler object
                        self.new_handler_object(module_name, handler_name)

                        # Search for message handler classes in the module
                        for name, cls in inspect.getmembers(sys.modules[module_namespace], predicate=inspect.isclass):
                            # Check if the class has been marked as message handlers
                            if hasattr(cls, '__handler'):
                                # Class is for message handlers, set handler object and iterate through functions
                                self.new_handler_object(name, handler_name, module_name)

                                # Iterate over class functions
                                for func_name, func in inspect.getmembers(cls, predicate=inspect.isfunction):
                                    # Function is a message handler
                                    # Set the type and add it to the current handler object
                                    self.new_handler_object(func_name, handler_name, module_name, name,
                                                            obj=asyncio.coroutine(func))

                                    log.debug(self.log_tag,
                                              'Imported  [ {} ]  Message Handler  [ {}.{} ]',
                                              module_namespace, name, func_name)

                # Error during module processing!
                except Exception as inst:
                    log.exception(self.log_tag,
                                  'Importing {} Message Handler  [ {} ]',
                                  inst, handler_name, file)

    def get_folders(self):
        # Make empty list for folder names
        folder_list = []

        # Walk through root handler dir and get handler folders
        for (root, dirs, files) in os.walk(self.root_folder):
            for folder in dirs:
                # Make sure we don't get the compiled code folder or something else magic
                if '__' not in folder:
                    folder_list.append(os.path.join(self.root_folder, folder))
            break

        # Return the folder list
        return folder_list


def message_handlers(cls):
    cls.__handler = True
    return cls