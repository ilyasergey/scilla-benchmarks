from Crypto.Hash import keccak
import uuid
from ecdsa import SigningKey, SECP256k1
import sha3
import json


def keccak256(string):
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(string)
    return keccak_hash.hexdigest()


def checksum_encode(addr_str):  # Takes a hex (string) address as input
    keccak = sha3.keccak_256()
    out = ''
    addr = addr_str.lower().replace('0x', '')
    keccak.update(addr.encode('ascii'))
    hash_addr = keccak.hexdigest()
    for i, c in enumerate(addr):
        if int(hash_addr[i], 16) >= 8:
            out += c.upper()
        else:
            out += c
    return '0x' + out


def generate_address():
    keccak = sha3.keccak_256()
    priv = SigningKey.generate(curve=SECP256k1)
    pub = priv.get_verifying_key().to_string()
    keccak.update(pub)
    address = keccak.hexdigest()[24:]
    return checksum_encode(address)


def generate_addresses(no_of_addresses):
    return [generate_address() for i in range(no_of_addresses)]


def get_addresses():
    addresses = None
    with open('addresses.json') as f:
        addresses = json.load(f)
    return addresses


if __name__ == '__main__':
    with open('addresses.json', 'w') as f:
        json.dump(generate_addresses(1000), f)
