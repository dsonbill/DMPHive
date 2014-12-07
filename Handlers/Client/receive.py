import os
from DarkPyNetwork import message_handling, log
from DarkPyNetwork.message_parsing import MessageReader


@message_handling.message_handlers
class ServerMessageType():
    @staticmethod
    def HANDSHAKE_CHALLANGE(client, msg):

        with MessageReader(msg.message_stream) as mr:
            challenge = yield from mr.read('bytes')
            signature = client.crsa.sign(challenge, 'SHA-256')
            yield from client.send(client.protocol.ClientMessageType.HANDSHAKE_RESPONSE, signature)

    @staticmethod
    def HEARTBEAT(client, msg):
        pass

    @staticmethod
    def HANDSHAKE_REPLY(client, msg):
        with MessageReader(msg.message_stream) as mr:
            reply = yield from mr.read('int')
            reason = yield from mr.read('str')
            server_protocol_version = yield from mr.read('int')
            server_version = yield from mr.read('str')

        # If we handshook successfully, the mod data will be available to read.
        if reply == 0:
            mod_control_mode = yield from mr.read('int')
            log.log(client.log_tag, 'Server Mod Control Mode Is  [ {} ]', mod_control_mode)
            # Check if server mod control is disabled
            if mod_control_mode != client.protocol.ModControlMode.DISABLED.value:
                mod_file_data = yield from mr.read('str')

        # Handshake was successful
        if reply == 0:
            log.log(client.log_tag, 'Client Handshake Successful')
            client.authenticated.set()
        else:
            disconnect_reason = "Handshake failure: " + reason
            # If it's a protocol mismatch, append the client/server version.
            if reply == 1:

                client_version = client.protocol.info.PROGRAM_VERSION
                # Trim git tags
                if len(client_version) == 40:
                    client_version = client.protocol.info.PROGRAM_VERSION[0, 7]
                if len(server_version) == 40:
                    server_version = server_version.Substring[0, 7]
                disconnect_reason += "\nClient: " + client_version + ", Server: " + server_version
                # If they both aren't a release version, display the actual protocol version.
                if not 'v' in server_version or not 'v' in client.protocol.info.PROGRAM_VERSION:
                    reason_protocol = '\nClient protocol: {}, Sever: {}'
                    if server_protocol_version != -1:
                        disconnect_reason += reason_protocol.format(client.protocol.info.PROTOCOL_VERSION,
                                                                    server_protocol_version)
                    else:
                        disconnect_reason += reason_protocol.format(client.protocol.info.PROTOCOL_VERSION,
                                                                    '8-')
            yield from client.disconnect(disconnect_reason)

    @staticmethod
    def VESSEL_PROTO(client, msg):
        with MessageReader(msg.message_stream) as mr:
            planetTime = yield from mr.read('double')
            vesselID = yield from mr.read('str')
            #Docking - don't care.
            yield from mr.read('bool')
            #Flying - don't care.
            yield from mr.read('bool')
            vesselData = yield from mr.read('str')
            log.log(client.log_tag, 'GOT VESSEL DATA: {}', vesselData)
            with open(os.path.join(client.data_dir, vesselID), 'w') as file:
                file.write(vesselData)
            #UniverseSyncCache.fetch.QueueToCache(vesselData); TEH ORIGINAL HAS A CACHE LIKE A COOL KID YO
            #ConfigNode vesselNode = ConfigNodeSerializer.fetch.Deserialize(vesselData); SOME SHIT YO
            #if (vesselNode != null)
            #{
            #    string vesselIDConfigNode = Common.ConvertConfigStringToGUIDString(vesselNode.GetValue("pid"));
            #    if ((vesselID != null) && (vesselID == vesselIDConfigNode))
            #    {
            #        VesselWorker.fetch.QueueVesselProto(vesselID, planetTime, vesselNode);
            #    }
            #    else
            #    {
            #        DarkLog.Debug("Failed to load vessel " + vesselID + "!");
            #    }
            #}
            #else
            #{
            #    DarkLog.Debug("Failed to load vessel" + vesselID + "!");
            #}

        #if (state == ClientState.SYNCING_VESSELS)
        #    if (numberOfVessels != 0)
        #        if (numberOfVesselsReceived > numberOfVessels)
        #            # Received 102 / 101 vessels!
        #            numberOfVessels = numberOfVesselsReceived;
        #        Client.fetch.status = "Syncing vessels " + numberOfVesselsReceived + "/" + numberOfVessels + " (" + (int)((numberOfVesselsReceived / (float)numberOfVessels) * 100) + "%)";



