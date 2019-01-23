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
SENDER_PRIVKEY = '4bc95d997c4c700bb4769678fa8452c2f67c9348e33f6f32b824253ae29a5316'


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


def get_addresses_from_file():
    addresses = None
    current_dir = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(current_dir, 'addresses.json')
    with open(filepath) as f:
        addresses = json.load(f)
    return addresses


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
    return keccak256(rlp.encode([normalize_address(sender), nonce]))[24:]


def get_addresses(no_of_addresses):
    address = [generate_contract_address(
        SENDER_ADDRESS, nonce) for nonce in range(no_of_addresses)]
    return address


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


addresses = get_addresses(10000)


def get_random_address(address):
    return random.choice(addresses)


def get_random_number(address):
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


def get_random_token_id(address):
    return random.randint(1, 20000)


if __name__ == '__main__':
    iterations = 5
    addresses = [generate_contract_address(
        SENDER_ADDRESS, i) for i in range(iterations)]
    print(addresses)
