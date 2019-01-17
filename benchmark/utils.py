from Crypto.Hash import keccak
import os
import uuid
from ecdsa import SigningKey, SECP256k1
import sha3
import json
import random


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
    addresses = []
    for i in range(no_of_addresses):
        if i % 100 == 0:
            print('Generated {} addresses'.format(i))
        addresses.append(generate_address())
    return addresses


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


addresses = get_addresses()


def get_random_address():
    return random.choice(addresses)


def get_random_number():
    return random.randint(1, 100000)


def use_value(val):
    def inner():
        return val
    return inner


def generate_random_params(arg_types):
    values = []
    for arg_type in arg_types:
        if arg_type == 'address':
            values.append(random.choice(get_addresses()))
        elif arg_type == 'string':
            values.append(str(uuid.uuid4()))
        else:
            values.append(random.randint(1, 100000))
    return values


def get_random_token_id():
    return random.randint(1, 20000)


if __name__ == '__main__':
    with open('addresses.json', 'w') as f:
        json.dump(generate_addresses(10000), f)
