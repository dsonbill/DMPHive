import os
import asyncio
import configparser

from DarkPyNetwork import client, loop_system


__author__ = 'William C. Donaldson'


if __name__ == '__main__':
    # Roos Directory
    root_dir = os.path.dirname(os.path.abspath(__file__))

    # asyncio Loop
    dloop = loop_system.DarkLoop()

    # Client Manager
    client_man = client.ClientManager(root_dir, 'Data', loop=dloop.main_loop)


    # Set end functions
    dloop.add_end_functions(client_man.disconnect_all)

    # Multi-Server DOS
    # Server Lists
    #servers = (['localhost'] * 4, [6702, 6703, 6704, 6705])
    #
    #for x in range(20):
    #    client_man.add_client('L33tS3rv3rDOSMAGIK{}'.format(x), multiconnect=True, client_count=len(servers[0]))
    #
    #for x in range(20):
    #    client_man.connect_client(servers[0], servers[1], 'L33tS3rv3rDOSMAGIK{}'.format(x))

    # Easy DOS
    #for x in range(20):
    #    client_man.add_client('L33tS3rv3rDOSMAGIK{}'.format(x))
    #    client_man.connect_client('localhost', 6702, name='L33tS3rv3rDOSMAGIK{}'.format(x))

    # Legitimate Clients
    client_man.add_client('PyCli')
    #client_man.add_client('PyCli2')

    client_man.connect_client('localhost', 6702, 'PyCli')
    #client_man.connect_client('localhost', 6702, 'PyCli2')

    # Run loop
    dloop.begin_main()