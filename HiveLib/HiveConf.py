import os
import configparser

__author__ = 'William C. Donaldson'

CONFIG = configparser.ConfigParser()

ROOTDIR = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
RPCDIR = os.path.join(ROOTDIR, 'Handlers', 'RPCHandlers')
SUBDIR = os.path.join(ROOTDIR, 'Handlers', 'SubHandlers')
CONFIGFILE = os.path.join(ROOTDIR, 'DMPHive.cfg')


def generate_default_config():
    CONFIG['LOGGING'] = {}
    CONFIG['LOGGING']['Debugging'] = 'False'
    try:
        with open(CONFIGFILE, 'w') as file:
            CONFIG.write(file)
    except Exception as inst:
        print('Encountered exception while trying to write configuration file!')


try:
    if CONFIG.read(CONFIGFILE) == []:
        print('No config file or config is empty! Loading defaults and generating DMPHive.cfg...')
        generate_default_config()

except Exception as inst:
    print('Error reading config file! Loading defaults and generating DMPHive.cfg...')
    generate_default_config()