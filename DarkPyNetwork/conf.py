import os
import inspect
import configparser


class Expando(object):
    pass


class DarkConfigManager():
    def __init__(self, data_root, main_config_name='main', main_config=None):
        # Check if the base directory exists
        if os.path.isdir(os.path.split(data_root)[0]):
            # Check if data_root exists
            if os.path.isdir(data_root):
                # Set data_root
                self.data_root = data_root
            else:
                # Data root does not exist! Raise an attribute exception.
                raise AttributeError('DarkConfigManager\'s data_root argument must be a valid path!')
        else:
            raise AttributeError('DarkConfigManager\'s data_root argument must reside within a valid path!')
        if main_config is None:
            main_config = configparser.ConfigParser()
            main_config['LOGGING'] = {}
            main_config['LOGGING']['debugging'] = 'False'
            main_config['HANDLERS'] = {}
            main_config['HANDLERS']['folder'] = 'Handlers'
            self.add_config('main')
            self.add_config_file('main', main_config_name, main_config)

    def scoped_config_function(self, func, config_name):
        def scoped_function(*args, **kwargs):
            func(self, config_name, *args, **kwargs)
        return scoped_function

    def add_config(self, config_name, obj=None):
        # Check if object is none
        if obj is None:
            obj = Expando()
        # add_config should not allow you to overwrite a config object
        if not self.config_exists(config_name):
            setattr(self, config_name, obj)

    def get_config(self, config_name):
        return getattr(self, config_name)

    def add_config_file(self, config_name, file_name, default_config):
        # add_config_file should not allow you to overwrite a config file
        # config_name is a relative path inside data_dir

        # Check if the config file exists as an object
        if not self.config_object_exists(config_name, file_name):

            # Get config object
            config_object = getattr(self, config_name)

            # Set config control functions
            config_object.add_config_file = self.scoped_config_function(self.add_config_file, config_name)
            config_object.save_config_file = self.scoped_config_function(self.save_config_file, config_name)

            # Make full path from file_name
            full_path = os.path.join(self.data_root, config_name)

            # If we are processing main, set it's path to data_root
            if config_name == 'main':
                # Create the config file
                config_file = DarkConfig(self.data_root, file_name + '.cfg')
                # Set the file to the config object
                setattr(self, file_name, config_file)
            else:
                # Check if full_path exists
                if not os.path.isdir(full_path) and not os.path.exists(full_path):
                    # Path does not exist, should be safe to create it
                    os.makedirs(full_path)

                # Create the config file
                config_file = DarkConfig(full_path, file_name + '.cfg')

                # Set the file to the config object
                setattr(config_object, file_name, config_file)

            # Check if we should save it to the disk
            if config_file.file_exists():
                # Configuration file exists, load it
                config_file.load_config()
            else:
                self.save_config_file(config_name, file_name, new_config=default_config)

    def save_config_file(self, config_name, file_name, new_config=None):
        # Check if the config object is valid
        if self.config_exists(config_name):

            # Get the config object
            config_object = getattr(self, config_name)

            # Check if the config file exists
            if self.config_object_exists(config_name, file_name) or config_name == 'main':

                # If we are processing main, set it's path to data_root
                if config_name == 'main':
                    config_file = getattr(self, file_name)
                else:
                    config_file = getattr(config_object, file_name)
                # Check if we are overwriting the config file
                if new_config is not None:
                    # Save config file to disk
                    config_file.set_config(new_config)
                    config_file.save_config()
                else:
                    config_file = getattr(config_object, file_name)
                    config_file.save_config()

            else:
                raise ReferenceError('DarkConfigManager tried to save a config file that does not exist!')

        else:
            raise AttributeError('DarkConfigManager tried to save a config file from an object that does not exist!')

    def config_exists(self, config_name):
        return hasattr(self, config_name)

    def config_object_exists(self, config_name, file_name):
        if self.config_exists(config_name):
            class_contents = inspect.getmembers(getattr(self, config_name))
            for object_tuple in class_contents:
                if file_name == object_tuple[0]:
                    return True
        return False


class DarkConfig():
    def __init__(self, data_root, config_name):
        # Variables
        self.loaded = False

        # Make the base config object
        self.config = configparser.ConfigParser()

        # Check if the base directory exists
        if os.path.isdir(os.path.split(data_root)[0]):

            # Check if data_root exists
            if os.path.isdir(data_root):

                # Set config_file and data_root
                self.config_file = os.path.join(data_root, config_name)
                self.data_root = data_root

            else:
                raise AttributeError('DarkConfig expects a valid existing directory as second argument!')

        else:
            raise AttributeError('DarkConfig expects a valid existing directory as second argument!')

    def file_exists(self):
        if os.path.isfile(self.config_file):
            return True
        else:
            return False

    def set_config(self, default_config_object):
        self.config = default_config_object
        self.loaded = True

    def load_config(self):
        # Make sure the file exists
        if self.file_exists():
            self.config.read(self.config_file, 'utf-8')
            self.loaded = True
        else:
            raise FileNotFoundError('DarkConfig tried to load a file that does not exist!')

    def save_config(self):
        if self.loaded:
            with open(self.config_file, mode='w', encoding='utf-8') as file:
                self.config.write(file)
        else:
            raise Exception('DarkConfig tried to save a file that has not been set!')