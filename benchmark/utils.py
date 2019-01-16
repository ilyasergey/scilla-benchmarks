from Crypto.Hash import keccak
import os
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
    current_dir = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(current_dir, 'addresses.json')
    with open(filepath) as f:
        addresses = json.load(f)
    return addresses


def get_directory_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


class ContractFunction():
    def __init__(self, name, arg_types):
        self.name = name
        self.arg_types = arg_types

    def get_signature(self):
        name_with_args = '{}({})'.format(self.name, ','.join(self.arg_types))
        signature = keccak256(name_with_args.encode('utf-8'))[:8]
        return signature


if __name__ == '__main__':
    with open('addresses.json', 'w') as f:
        json.dump(generate_addresses(1000), f)
