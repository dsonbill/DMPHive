import os
import configparser


CONFIG = configparser.ConfigParser()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIGFILE = os.path.join(ROOT_DIR, 'client.cfg')


def generate_default_config():
    CONFIG['GENERAL'] = {}
    CONFIG['GENERAL']['datadir'] = 'Data'
    CONFIG['LOGGING'] = {}
    CONFIG['LOGGING']['debugging'] = 'True'
    CONFIG['HANDLERS'] = {}
    CONFIG['HANDLERS']['root'] = 'Handlers'
    CONFIG['KEYPAIR'] = {}
    CONFIG['KEYPAIR']['Private'] = 'PrivKey.xml'


def write_config():
    try:
        with open(CONFIGFILE, 'w') as file:
            CONFIG.write(file)
    except Exception as inst:
        print('Encountered exception while trying to write configuration file!')

try:
    if not CONFIG.read(CONFIGFILE):
        print('No config file or config is empty! Loading defaults and generating client.cfg...')
        generate_default_config()
        write_config()

except Exception as inst:
    print('Error reading config file! Loading defaults...')
    generate_default_config()