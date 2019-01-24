try:
    from Crypto.Hash import keccak

    def sha3_256(x): return keccak.new(digest_bits=256, data=x).digest()
except:
    import sha3 as _sha3

    def sha3_256(x): return _sha3.sha3_256(x).digest()
import os
import uuid
from ecdsa import SigningKey, SECP256k1
import rlp
from rlp.utils import decode_hex, encode_hex, ascii_chr, str_to_bytes
import json
import random

SENDER_ADDRESS = '0xfaB8FcF1b5fF9547821B4506Fa0C35c68a555F90'
BASE_ADDRESS = '0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE'


def to_string(value):
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return bytes(value, 'utf-8')
    if isinstance(value, int):
        return bytes(str(value), 'utf-8')


def sha3(seed):
    return sha3_256(to_string(seed))


def keccak256(string):
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(string)
    return keccak_hash.hexdigest()


def normalize_address(x, allow_blank=False):
    if allow_blank and x == '':
        return ''
    if len(x) in (42, 50) and x[:2] == '0x':
        x = x[2:]
    if len(x) in (40, 48):
        x = decode_hex(x)
    if len(x) == 24:
        assert len(x) == 24 and keccak256(x[:20])[:4] == x[-4:]
        x = x[:20]
    if len(x) != 20:
        raise Exception("Invalid address format: %r" % x)
    return x


def generate_contract_address(sender, nonce):
    return '0x'+keccak256(rlp.encode([normalize_address(sender), nonce]))[24:]


def get_addresses(no_of_addresses):
    return [generate_contract_address(BASE_ADDRESS, i)
            for i in range(no_of_addresses)]


addresses = get_addresses(30000)


if __name__ == '__main__':
    iterations = 5
    addresses = [generate_contract_address(
        SENDER_ADDRESS, i) for i in range(iterations)]
    print(addresses)
