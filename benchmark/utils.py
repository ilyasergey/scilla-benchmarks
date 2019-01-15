from Crypto.Hash import keccak
import uuid


def keccak256(string):
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(string)
    return keccak_hash.hexdigest()


def generate_address():
    return keccak256(str(uuid.uuid4))
