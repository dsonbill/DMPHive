import asyncio
from DarkPyNetwork import log, message_handling
from DarkPyNetwork.message_parsing import MessageWriter, NetworkMessage


@message_handling.message_handlers
class ClientMessageType():

    @staticmethod
    def CONNECTION_END(client, reason='Unknown'):
        # Log Disconnection
        log.log(client.log_tag,
                "Sending Disconnect Message, Reason: {}", reason)

        # Write the disconnect message
        with MessageWriter() as mw:
            mw.write('str', reason)
            msg = NetworkMessage()
            msg.set_header(client.protocol.ClientMessageType,
                           client.protocol.ClientMessageType.CONNECTION_END)
            yield from msg.write(client.writer, mw.data)
        yield from client.close_connection()

    @staticmethod
    def HEARTBEAT(client):
        yield from asyncio.sleep(client.protocol.info.HEART_BEAT_INTERVAL/1000, loop=client.loop)  # Lol. Wut.

        msg = NetworkMessage()
        msg.set_header(client.protocol.ClientMessageType,
                       client.protocol.ClientMessageType.HEARTBEAT)
        yield from msg.write(client.writer)

    @staticmethod
    def HANDSHAKE_RESPONSE(client, signature):
        with MessageWriter() as mw:
            mw.write('int', client.protocol.info.PROTOCOL_VERSION)
            mw.write('str', client.name)
            mw.write('str', client.crsa.public_key_xml)
            mw.write('bytes', signature)
            mw.write('str', client.protocol.info.PROGRAM_VERSION)
            msg = NetworkMessage()
            msg.set_header(client.protocol.ClientMessageType,
                           client.protocol.ClientMessageType.HANDSHAKE_RESPONSE)
            yield from msg.write(client.writer, mw.data)