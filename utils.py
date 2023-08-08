from web3 import Web3
from eth_typing import ChecksumAddress


def to_checksum(address: str) -> ChecksumAddress:
    return Web3.to_checksum_address(address)
