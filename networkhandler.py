import os

import clientlog


class HandlerImporter():
    def __init__(self, folder, MESSAGE_HANDLERS, log_tag='IMPORT'):
        self.root_folder = folder
        self.MESSAGE_HANDLERS = MESSAGE_HANDLERS
        self.log_tag = log_tag
        self.lib_list = []
        for folder in self.get_folders():
            self.handler_import(folder)

    def handler_import(self, folder):
        # Import Handlers
        for (root, dirs, files) in os.walk(folder):
            # Get relative handler path and build module namespace
            handle_folder = os.path.basename(os.path.normpath(os.path.dirname(os.path.abspath(root))))
            handle_name = '{}.{}'.format(handle_folder, os.path.basename(os.path.normpath(root)))
            # If there is a file called standard.py in the folder, move it to the front of the import list.
            if 'standard.py' in files:
                files.insert(0, files.pop(files.index('standard.py')))
            else:
                clientlog.debug(self.log_tag, 'Standard Message Library Not Found! Skipping List Reorder.')

            for file in files:
                try:
                    module_name = os.path.splitext(file)[0]
                    __import__('{}.{}'.format(handle_name, module_name),
                               globals(),
                               locals(),
                               fromlist=[handle_name])
                    clientlog.log(self.log_tag, 'Imported Message Handler  [ {} ]', module_name)
                except Exception as inst:
                    clientlog.error(self.log_tag, 'Exception  [ {} ]  Importing Message Handler  [ {} ]', type(inst), file)
            break

    def get_folders(self):
        # Make empty list for folder names
        folder_list = []
        # Walk through root handler dir and get handler folders
        for (root, dirs, files) in os.walk(self.root_folder):
            for folder in dirs:
                if '__' not in folder:
                    folder_list.append(os.path.join(self.root_folder, folder))
            break
        # Return the folder list
        return folder_list