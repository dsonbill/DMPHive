import os
import Common
import handleregister
import clientconf
import xmlrsa
from messagewriter import message_reader, message_writer, NetworkMessage

@handleregister.message_handler
@Common.server_network_message
def HANDSHAKE_CHALLANGE(message_stream, write_stream):
    private_key_file = os.path.join(clientconf.ROOT_DIR, clientconf.CONFIG['KEYPAIR']['Private'])
    if os.path.isfile(private_key_file):
        crsa = xmlrsa.RSA()
        crsa.load_keys_xml(private_key_file)
    else:
        crsa = xmlrsa.RSA(1024)
        crsa.save_keys_xml(private_key_file)
    with message_reader(message_stream) as dr:
        challenge = yield from dr.read('bytes')
        signature = crsa.sign(challenge, 'SHA-256')
    with message_writer() as dw:
        dw.write('int', 30)
        dw.write('str', 'PyClient')
        dw.write('str', crsa.public_key_xml)
        dw.write('bytes', signature)
        dw.write('str', Common.PROGRAM_VERSION)
        msg = NetworkMessage(Common.ClientMessageType.HANDSHAKE_RESPONSE)
        yield from msg.send(write_stream, dw.data)