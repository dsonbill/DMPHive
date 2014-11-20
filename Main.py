import os
import asyncio
import handleregister
import clientconf
import networkhandler
import client
import Common

__author__ = 'William C. Donaldson'


if __name__ == '__main__':

    handler_importer = networkhandler.HandlerImporter(os.path.join(clientconf.ROOT_DIR,
                                                                   clientconf.CONFIG['HANDLERS']['root']),
                                                      handleregister.MESSAGE_HANDLERS)

    loop = asyncio.get_event_loop()
    DMPClient = client.AsyncTCPClient(Common.HEART_BEAT_INTERVAL/1000, handleregister.MESSAGE_HANDLERS, loop)
    @asyncio.coroutine
    def easy_start(client_control):

        yield from DMPClient.add_server('localhost', '127.0.0.1', 6702)
        asyncio.async(DMPClient.connect('localhost'))

    asyncio.async(DMPClient.client(easy_start))
    loop.run_forever()






