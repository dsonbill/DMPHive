import rsa
import base64
import math
import xml.etree.ElementTree as ET


# Utility functions
def bytes_to_int(byte_data):
    return int.from_bytes(byte_data, 'big')


def bytes_from_int(integer):
    byte_length = math.ceil(integer.bit_length() / 8)
    return integer.to_bytes(byte_length, 'big')


class RSA():
    def __init__(self, key_size=None):
        if key_size is not None:
            self.public_key, self.private_key = rsa.newkeys(key_size)
            self.public_key_xml, self.private_key_xml = self.get_keys_xml_string(self.private_key)
            self.initialized = True

    def sign(self, message, hash):
        if self.initialized:
            return rsa.sign(message, self.private_key, hash)

    def verify(self, message, signature):
        if self.initialized:
            return rsa.verify(message, signature, self.public_key)

    def load_keys_xml(self, filename_private_key):
        # Build public and private key object
        rsa_xml = ET.parse(filename_private_key).getroot()
        modulus_xml = rsa_xml.find('Modulus')
        exponent_xml = rsa_xml.find('Exponent')
        d_xml = rsa_xml.find('D')
        p_xml = rsa_xml.find('P')
        q_xml = rsa_xml.find('Q')

        modulus_int = bytes_to_int(base64.standard_b64decode(modulus_xml.text))
        modulus_bytes = base64.standard_b64decode(modulus_xml.text)
        modulus_bytes_tested = bytes_from_int(bytes_to_int(modulus_bytes))
        if modulus_bytes == modulus_bytes_tested:
            print("Everything is good")

        exponent_int = bytes_to_int(base64.standard_b64decode(exponent_xml.text))
        d_int = bytes_to_int(base64.standard_b64decode(d_xml.text))
        p_int = bytes_to_int(base64.standard_b64decode(p_xml.text))
        q_int = bytes_to_int(base64.standard_b64decode(q_xml.text))

        # Set key objects
        self.public_key = rsa.PublicKey(modulus_int, exponent_int)
        self.private_key = rsa.PrivateKey(modulus_int, exponent_int, d_int, p_int, q_int)

        # Set key xml strings
        self.public_key_xml, self.private_key_xml = self.get_keys_xml_string(self.private_key)

        # Set initialized flag
        self.initialized = True

    def save_keys_xml(self, filename_private_key):
        if self.initialized:
            with open(filename_private_key, 'w') as file:
                file.write(self.private_key_xml)

    @staticmethod
    def get_keys_xml_string(private_key):
        rsa_key_value_xml = ET.Element('RSAKeyValue')
        modulus_xml = ET.SubElement(rsa_key_value_xml, 'Modulus')
        exponent_xml = ET.SubElement(rsa_key_value_xml, 'Exponent')

        modulus_xml.text = base64.standard_b64encode(bytes_from_int(private_key.n)).decode("utf-8")
        exponent_xml.text = base64.standard_b64encode(bytes_from_int(private_key.e)).decode("utf-8")

        pubkey = ET.tostring(rsa_key_value_xml).decode('utf-8')

        d_xml = ET.SubElement(rsa_key_value_xml, 'D')
        p_xml = ET.SubElement(rsa_key_value_xml, 'P')
        q_xml = ET.SubElement(rsa_key_value_xml, 'Q')
        dp_xml = ET.SubElement(rsa_key_value_xml, 'DP')
        dq_xml = ET.SubElement(rsa_key_value_xml, 'DQ')
        inverseq_xml = ET.SubElement(rsa_key_value_xml, 'InverseQ')

        d_xml.text = base64.standard_b64encode(bytes_from_int(private_key.d)).decode("utf-8")
        p_xml.text = base64.standard_b64encode(bytes_from_int(private_key.p)).decode("utf-8")
        q_xml.text = base64.standard_b64encode(bytes_from_int(private_key.q)).decode("utf-8")
        dp_xml.text = base64.standard_b64encode(bytes_from_int(private_key.exp1)).decode('utf-8')
        dq_xml.text = base64.standard_b64encode(bytes_from_int(private_key.exp2)).decode('utf-8')
        inverseq_xml.text = base64.standard_b64encode(bytes_from_int(private_key.coef)).decode('utf-8')

        privkey = ET.tostring(rsa_key_value_xml).decode('utf-8')

        return pubkey, privkey

