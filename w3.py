from web3 import Web3
from erc20 import erc20
from typing import Optional

provider = Web3(Web3.HTTPProvider("http://localhost:8545"))
address = provider.to_checksum_address("0xd8da6bf26964af9d7eed9e03e53415d37aa96045")
usdc = provider.to_checksum_address("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")

max_uint256 = 2**256 - 1
provider.eth.default_account = address


def fork_chain() -> Optional[str]:
    res = provider.provider.make_request("evm_snapshot", [])
    result = res.get("result")
    return result

    provider.provider.make_request("anvil_setBalance", [address, hex(max_uint256)])
    return result


def impersonate_account(account: str):
    res = provider.provider.make_request("anvil_impersonateAccount", [account])
    print(res)


def teardown(snapshot_id):
    res = provider.provider.make_request("evm_revert", [snapshot_id])
    print(res)


def get_token_balance(token_address, owner):
    contract = provider.eth.contract(
        address=token_address,
        abi=erc20,
    )
    return contract.functions.balanceOf(owner).call()


def approve(token_address, spender, amount=max_uint256):
    contract = provider.eth.contract(
        address=token_address,
        abi=erc20,
    )
    res = contract.functions.approve(spender, amount).transact()
    trx = provider.eth.wait_for_transaction_receipt(res)
    return True if trx["status"] == 1 else False


def transfer(token_address, to, amount):
    contract = provider.eth.contract(
        address=token_address,
        abi=erc20,
    )
    transfer_hash = contract.functions.transfer(to, amount).transact()
    trx = provider.eth.wait_for_transaction_receipt(transfer_hash)
    return True if trx["status"] == 1 else False


def setup():
    account = provider.eth.account.create()
    provider.eth.default_account = address
    print(provider.eth.default_account)
    balb4 = provider.eth.get_balance(address)
    tx = {
        "to": account.address,
        "value": 10 * 10**18,
        "gasPrice": provider.to_wei("100", "gwei"),
        "gas": 200000,
        "nonce": provider.eth.get_transaction_count(address),
    }
    hash = provider.eth.send_transaction(tx)
    provider.eth.wait_for_transaction_receipt(hash)
    balaf = provider.eth.get_balance(address)
    # signed = provider.eth.account.sign_transaction(tx)

    print(balb4 - balaf)
    # print(accounts)
    return

    snap_id = fork_chain()

    print(provider.eth.get_balance(address))
    teardown(snap_id)


# print(provider.eth.chain_id)
# print(provider.eth.get_block("latest"))
# bal = provider.eth.get_balance(address)
# print(bal)
# print(provider.is_connected())
# get_token_balance(usdc, address)
# print(fork_chain())
# print(setup())
# teardown("0x1")
# print(approve(usdc, provider.eth.accounts[2]))
