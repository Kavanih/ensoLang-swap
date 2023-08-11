import requests
from web3 import Web3
from eth_typing import ChecksumAddress
import os, json
import dotenv
from w3 import (
    provider,
    approve,
    fork_chain,
    teardown,
    get_token_balance,
    address as from_address,
    provider,
    check_approval,
)
from utils import to_checksum
from web3.types import TxParams

dotenv.load_dotenv()

node_url = "https://arb1.arbitrum.io/rpc"
privateKey = os.getenv("PRIVATE_KEY")

w3 = Web3(Web3.HTTPProvider(node_url))


account = w3.eth.account.from_key(privateKey)
usdt = "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"
usdc = "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"
arb = "0x912CE59144191C1204E64559FE8253a0e49E6548"
chain_id = w3.eth.chain_id
amount_in = 1 * 10**18
vitalik = w3.to_checksum_address(from_address)

ausdc = w3.to_checksum_address("0x9ba00d6856a4edf4665bca2c2309936572473b7e")
aaveV2LendingPool = w3.to_checksum_address("0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9")
usdc = w3.to_checksum_address("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
dai = w3.to_checksum_address("0x6b175474e89094c44da98b954eedeac495271d0f")
usdcAmount = w3.to_wei("1000", "mwei")
daiAmount = w3.to_wei("500", "ether")
# print(approve(usdc, wallet))


class EnsoFinance:
    base_url: str = "https://api.enso.finance/api/v1"
    key: str = "1e02632d-6feb-4a75-a157-documentation"
    url: str = "https://api.enso.finance/api/v1/shortcuts/bundle"

    def account_wallet(self, address, chain_id):
        url = f"{self.base_url}/wallet?chainId={chain_id}&fromAddress={address}"
        res = requests.get(url)

        if res.status_code != 200:
            print(res.json()["message"])
            raise ValueError("Unable to get account wallet")
        data = res.json()
        return data

    def check_allowance(self, token_address, owner, spender) -> int:
        approval = check_approval(token_address, owner, spender)
        return approval

    def approve(self, chain_id, account, token_address, amount):
        params = {
            "chainId": chain_id,
            "fromAddress": to_checksum(account),
            "tokenAddress": to_checksum(token_address),
            "amount": amount,
        }

        url = self.base_url + "/wallet/approve"
        res = requests.get(url, params=params)

        if res.status_code != 200:
            return res.json()

        trx = res.json()["tx"]
        trx["value"] = int(trx.get("value", 0))
        trx["gas"] = 100000000000
        trx["gasPrice"] = provider.eth.gas_price
        nonce = provider.eth.get_transaction_count(to_checksum(account))
        trx["nonce"] = nonce

        try:
            gas = provider.eth.estimate_gas(trx)
        except Exception as e:
            return {
                "status": "error",
                "message": "Failed to estimate gas for approve transaction",
            }

        trx["gas"] = gas
        return trx
        # tnx = w3.eth.account.sign_transaction(trx, privateKey)
        # res = w3.eth.send_raw_transaction(tnx.rawTransaction)
        # w3.eth.wait_for_transaction_receipt(res)
        return True

    def swap(self, chain_id, account, token_in, amount, token_out):
        self.approve(chain_id, account, token_in, amount)
        _url = f"{self.base_url}/shortcuts/route"
        print(account.address)
        print(self.key)
        print(chain_id)
        params = {
            "chainId": chain_id,
            "fromAddress": account.address,
            "slippage": 300,
            "tokenIn": token_in,
            "tokenOut": token_out,
            "amountIn": amount,
            "tokenInAmountToApprove": amount,
            "toEoa": True,
        }

        res = requests.get(
            _url,
            params=params,
            headers={"Authorization": f"Bearer {self.key}"},
        )

        if res.status_code != 200:
            raise ValueError(res.json()["message"])

        data = res.json()
        trx = data["tx"]
        trx["value"] = int(trx["value"])
        trx["gas"] = 5500000000
        trx["gasPrice"] = w3.eth.gas_price
        nonce = w3.eth.get_transaction_count(account.address)
        trx["nonce"] = nonce

        try:
            gas = w3.eth.estimate_gas(trx)
        except Exception as e:
            raise ValueError("Failed to estimate gas for transaction ")

        trx["gas"] = gas
        tnx = w3.eth.account.sign_transaction(trx, privateKey)
        res = w3.eth.send_raw_transaction(tnx.rawTransaction)
        print(f"Swap done: trx hash: {res.hex()}")

    def borrow(
        self,
        chain_id: int,
        collateral: ChecksumAddress,
        token: ChecksumAddress,
        from_address: ChecksumAddress,
        amount: int,
    ) -> TxParams:
        token = to_checksum(token)
        collateral = to_checksum(collateral)
        from_address = to_checksum(from_address)

        walletRes = self.account_wallet(from_address, chain_id)
        wallet = w3.to_checksum_address(walletRes["address"])
        balance = get_token_balance(token, from_address)
        allowance = self.check_allowance(token, from_address, wallet)

        if amount > balance:
            raise ValueError("Insufficient Balance")

        data = [
            {
                "protocol": "erc20",
                "action": "transferfrom",
                "args": {
                    "sender": from_address,
                    "recipient": wallet,
                    "token": collateral,
                    "amount": amount,
                },
            },
            {
                "protocol": "aave-v2",
                "action": "deposit",
                "args": {
                    "tokenIn": collateral,
                    "tokenOut": ausdc,
                    "amountIn": amount,
                    "primaryAddress": aaveV2LendingPool,
                },
            },
            {
                "protocol": "aave-v2",
                "action": "borrow",
                "args": {
                    "collateral": collateral,
                    "tokenOut": token,
                    "amountOut": amount,
                    "primaryAddress": aaveV2LendingPool,
                    "toEao": True,
                },
            },
        ]
        params = {
            "chainId": chain_id,
            "fromAddress": from_address,
            "toEoa": True,
        }
        res = requests.post(
            f"https://api.enso.finance/api/v1/shortcuts/bundle",
            params=params,
            data=json.dumps(data),
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
        )
        data = res.json()

        return data["tx"]
        tx = data.get("tx")
        tx["value"] = int(tx["value"])
        tx["gasPrice"] = provider.eth.gas_price
        tx["gas"] = 10000000000
        tx["nonce"] = provider.eth.get_transaction_count(from_address)
        tx["gas"] = provider.eth.estimate_gas(tx)
        balb4 = get_token_balance(dai, wallet)
        trx = provider.eth.send_transaction(tx)
        res = provider.eth.wait_for_transaction_receipt(trx)
        print(res["status"])
        balaf = get_token_balance(dai, wallet)
        print(balaf - balb4)

    def lend(
        self,
        chain_id: int,
        token: ChecksumAddress,
        from_address: ChecksumAddress,
        amount: int,
    ) -> TxParams:
        token = to_checksum(token)
        from_address = to_checksum(from_address)
        walletRes = self.account_wallet(from_address, chain_id)
        wallet = w3.to_checksum_address(walletRes["address"])
        data = [
            {
                "protocol": "erc20",
                "action": "transferfrom",
                "args": {
                    "sender": from_address,
                    "recipient": wallet,
                    "token": token,
                    "amount": amount,
                },
            },
            {
                "protocol": "aave-v2",
                "action": "deposit",
                "args": {
                    "tokenIn": token,
                    "tokenOut": ausdc,
                    "amountIn": amount,
                    "primaryAddress": aaveV2LendingPool,
                },
            },
        ]
        params = {
            "chainId": chain_id,
            "fromAddress": from_address,
            "toEoa": True,
        }
        res = requests.post(
            f"https://api.enso.finance/api/v1/shortcuts/bundle",
            params=params,
            data=json.dumps(data),
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
        )
        data = res.json()
        return data
        pass


if __name__ == "__main__":
    enso = EnsoFinance()
    # enso.swap(chain_id, account, arb, amount_in, usdt)
    snapshot_id = None
    try:
        snapshot_id = fork_chain()
        enso.borrow(1, vitalik)
    except Exception as e:
        print(e)

    finally:
        if snapshot_id:
            print(snapshot_id)
        teardown(snapshot_id)
